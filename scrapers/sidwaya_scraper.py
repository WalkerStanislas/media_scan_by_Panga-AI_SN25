"""
Scraper for Sidwaya.info - Burkina Faso news website
Site basé sur WordPress avec thème tagDiv
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import sys
from pathlib import Path
import re
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseMediaScraper
from config.settings import MEDIA_SOURCES, SCRAPING_CONFIG, RAW_DATA_DIR


class SidwayaScraper(BaseMediaScraper):
    """
    Scraper pour Sidwaya.info
    Site WordPress moderne avec structure tagDiv
    """

    name = 'sidwaya_scraper'
    media_name = "Sidwaya"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('sidwaya', {})
        self.base_url = self.config.get('base_url', 'https://www.sidwaya.info')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "sidwaya_articles.json"): {
                "format": "json",
                "encoding": "utf8",
                "overwrite": False,
            },
        },
        "USER_AGENT": SCRAPING_CONFIG.get('user_agent', 'Mozilla/5.0'),
        "DOWNLOAD_DELAY": SCRAPING_CONFIG.get('download_delay', 2),
        "ROBOTSTXT_OBEY": SCRAPING_CONFIG.get('robotstxt_obey', True),
        "LOG_LEVEL": "INFO",
        "CONCURRENT_REQUESTS": 2,
    }

    def start_requests(self):
        """
        Génère les requêtes pour les pages de Sidwaya
        Structure: https://www.sidwaya.info/bfcategories/[categorie]/page/X/
        """
        self.logger.info(f"Démarrage du scraper pour {self.media_name}")

        # Catégories principales du site
        categories = [
            'politique',
            'economie',
            'societe',
            'focus',
            'international/diplomatie',
            'international/politique-international',
            'sport',
            'culture',
            'sante',
            'education',
            "nouvelle-du-front",
        ]

        for category in categories:
            # Page 1 (sans /page/)
            yield scrapy.Request(
                url=f"{self.base_url}/bfcategories/{category}/",
                callback=self.parse_article_list,
                meta={'category': category, 'page_num': 1},
                errback=self.handle_error
            )
            
            # Pages suivantes
            for page in range(2, self.max_pages + 1):
                yield scrapy.Request(
                    url=f"{self.base_url}/bfcategories/{category}/page/{page}/",
                    callback=self.parse_article_list,
                    meta={'category': category, 'page_num': page},
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse la page de liste d'articles
        Structure: <div class="td_module_1"> contient les articles
        """
        category = response.meta.get('category')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse de {category} - page {page_num}")

        # Extraire les liens d'articles
        # Structure: <h3 class="entry-title td-module-title"><a href="URL">
        article_links = response.xpath(
            '//h3[contains(@class, "entry-title") and contains(@class, "td-module-title")]//a/@href'
        ).getall()

        self.logger.info(f"Trouvé {len(article_links)} articles sur la page {page_num}")

        for link in article_links:
            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={'category': category},
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        Structure WordPress/tagDiv de Sidwaya
        """
        self.logger.info(f"Extraction de l'article: {response.url}")

        # Extraire le titre
        # Plusieurs méthodes possibles
        title = (
            response.xpath('//h1[@class="entry-title"]//text()').get() or
            response.xpath('//meta[@property="og:title"]/@content').get() or
            response.xpath('//h1//text()').get()
        )

        # Extraire l'auteur
        # Structure: <div class="td-post-author-name"><a>Nom Auteur</a>
        author = response.xpath(
            '//div[@class="td-post-author-name"]//a/text()'
        ).get()
        
        if not author:
            # Fallback: meta author
            author = response.xpath('//meta[@name="author"]/@content').get()

        # Extraire la date de publication
        # Structure: <time class="entry-date" datetime="2025-10-16T00:34:26+00:00">
        date_raw = response.xpath(
            '//time[@class="entry-date updated td-module-date"]/@datetime'
        ).get()
        
        if not date_raw:
            # Fallback
            date_raw = response.xpath('//time/@datetime').get()
        
        publication_date = self.parse_iso_date(date_raw) if date_raw else ""

        # Extraire le contenu principal
        # Le contenu est dans <div class="td-post-content"> ou similaire
        content_paragraphs = response.xpath(
            '//div[contains(@class, "td-post-content")]//p//text() | '
            '//div[contains(@class, "td-post-content")]//p/strong//text() | '
            '//div[contains(@class, "td-post-content")]//p/em//text()'
        ).getall()

        if not content_paragraphs:
            # Fallback: article content
            content_paragraphs = response.xpath(
                '//article//div[contains(@class, "entry-content")]//p//text()'
            ).getall()

        # Nettoyer et joindre le contenu
        content = self.clean_article_content(content_paragraphs)

        # Extraire l'image principale
        image_url = (
            response.xpath('//meta[@property="og:image"]/@content').get() or
            response.xpath('//article//img[@class="entry-thumb"]/@src').get() or
            response.xpath('//div[contains(@class, "td-post-featured-image")]//img/@src').get()
        )

        # Extraire les tags/catégories
        tags = response.xpath(
            '//ul[@class="td-tags"]//a/text()'
        ).getall()

        # Préparer les données de l'article
        article_data = {
            'title': title.strip() if title else "",
            'author': author.strip() if author else "",
            'date_publication': publication_date,
            'post': content,
            'url': response.url,
            'image_url': image_url if image_url else "",
            'category': response.meta.get('category', ''),
            'tags': tags,
            'comments': [],
            'likes': 0,
            'partages': 0,
        }

        # Formater et retourner
        formatted_article = self.format_article(article_data)
        self.article_count += 1
        
        # Log avec aperçu
        content_preview = content[:100] + "..." if len(content) > 100 else content
        self.logger.info(
            f"Article extrait ({self.article_count}): "
            f"{title[:50] if title else 'Sans titre'}..."
        )
        self.logger.info(f"Contenu: {len(content)} caractères")

        yield formatted_article

    def clean_article_content(self, paragraphs):
        """
        Nettoie le contenu de l'article
        """
        cleaned = []
        
        for para in paragraphs:
            text = para.strip()
            
            # Ignorer les textes vides ou très courts
            if len(text) < 3:
                continue
            
            # Ignorer les éléments de navigation/UI
            if any(skip in text.lower() for skip in [
                'cliquez ici',
                'lire aussi',
                'voir aussi',
                'partager',
                'tweet',
                'facebook',
                'whatsapp',
            ]):
                continue
            
            cleaned.append(text)
        
        # Joindre avec double saut de ligne pour séparer les paragraphes
        return '\n\n'.join(cleaned)

    def parse_iso_date(self, date_str):
        """
        Parse les dates ISO 8601 de Sidwaya
        Format: "2025-10-16T00:34:26+00:00"
        """
        if not date_str:
            return ""
        
        try:
            # Supprimer le timezone pour simplifier
            date_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
            
            # Parser la date
            dt = datetime.fromisoformat(date_clean)
            
            # Format de sortie: YYYY-MM-DD HH:MM:SS
            return dt.strftime('%Y-%m-%d %H:%M:%S')
            
        except Exception as e:
            self.logger.warning(f"Erreur lors du parsing de la date '{date_str}': {e}")
            return date_str

    def handle_error(self, failure):
        """
        Gestion des erreurs de requête
        """
        self.logger.error(f"Échec de la requête: {failure.request.url}")
        self.logger.error(f"Raison: {failure.value}")


def run_scraper(max_pages=10):
    """
    Exécute le scraper Sidwaya
    """
    process = CrawlerProcess()
    process.crawl(SidwayaScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Scraper d\'articles depuis Sidwaya.info'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages à scraper par catégorie (défaut: 10)'
    )

    args = parser.parse_args()

    print(f"Démarrage du scraper Sidwaya...")
    print(f"Pages max par catégorie: {args.max_pages}")
    print(f"URL de base: https://www.sidwaya.info")
    print(f"Catégories: politique, economie, societe, focus, international, sport, culture, etc.")

    run_scraper(max_pages=args.max_pages)

    print("Scraping terminé!")