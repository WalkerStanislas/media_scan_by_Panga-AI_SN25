"""
Scraper for AIB Media (aib.media) - Agence d'Information du Burkina
Site WordPress avec thème Newspaper (tagDiv)
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


class AIBScraper(BaseMediaScraper):
    """
    Scraper pour AIB Media (Agence d'Information du Burkina)
    Site WordPress moderne avec thème Newspaper
    """

    name = 'aib_scraper'
    media_name = "AIB Media"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('aib', {})
        self.base_url = self.config.get('base_url', 'https://www.aib.media')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "aib_articles.json"): {
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
        Génère les requêtes pour les pages d'AIB Media
        Structure: https://www.aib.media/category/[categorie]/page/X/
        """
        self.logger.info(f"Démarrage du scraper pour {self.media_name}")

        # Catégories principales du site
        # Note: AIB a des sous-domaines (regions.aib.media) mais on se concentre sur le principal
        categories = [
            'depeches',
            'evenements',
            'medias',
            'politique',
            'economie',
            'societe',
            'culture',
            'sports',
            'international',
        ]

        for category in categories:
            # Page 1 (sans /page/)
            yield scrapy.Request(
                url=f"{self.base_url}/category/{category}/",
                callback=self.parse_article_list,
                meta={'category': category, 'page_num': 1},
                errback=self.handle_error
            )
            
            # Pages suivantes
            for page in range(2, self.max_pages + 1):
                yield scrapy.Request(
                    url=f"{self.base_url}/category/{category}/page/{page}/",
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
        # Structure AIB: <h3 class="entry-title td-module-title"><a href="URL">
        article_links = response.xpath(
            '//h3[contains(@class, "entry-title") and contains(@class, "td-module-title")]//a/@href'
        ).getall()

        # Aussi depuis les modules td_module_mx4 (sidebar)
        if not article_links:
            article_links = response.xpath(
                '//div[contains(@class, "td_module")]//h3[@class="entry-title td-module-title"]//a/@href'
            ).getall()

        self.logger.info(f"Trouvé {len(article_links)} articles sur la page {page_num}")

        # Dédupliquer les liens (éviter les doublons)
        unique_links = list(dict.fromkeys(article_links))

        for link in unique_links:
            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={'category': category},
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        Structure WordPress/Newspaper d'AIB Media
        """
        self.logger.info(f"Extraction de l'article: {response.url}")

        # Extraire le titre
        title = (
            response.xpath('//h1[@class="entry-title"]//text()').get() or
            response.xpath('//h1[contains(@class, "tdb-title-text")]//text()').get() or
            response.xpath('//meta[@property="og:title"]/@content').get() or
            response.xpath('//title/text()').get()
        )

        # Extraire l'auteur
        # Structure: <div class="td-post-author-name"><a>Nom</a>
        author = response.xpath(
            '//div[@class="td-post-author-name"]//a/text() | '
            '//a[@rel="author"]/text() | '
            '//span[@class="td-post-author-name"]//text()'
        ).get()
        
        if not author:
            # Meta author
            author = response.xpath('//meta[@name="author"]/@content').get()

        # Extraire la date de publication
        # Structure: <time class="entry-date" datetime="2025-11-15T15:47:51+01:00">
        date_raw = response.xpath(
            '//time[@class="entry-date updated td-module-date"]/@datetime | '
            '//time[@class="entry-date"]/@datetime | '
            '//span[@class="td-post-date"]//time/@datetime'
        ).get()
        
        if not date_raw:
            # Texte de la date
            date_raw = response.xpath(
                '//time[@class="entry-date"]/text() | '
                '//span[@class="td-post-date"]//time/text()'
            ).get()
        
        publication_date = self.parse_iso_date(date_raw) if date_raw else ""

        # Extraire le contenu principal
        # AIB utilise différentes structures selon le type d'article
        content_paragraphs = response.xpath(
            '//div[contains(@class, "td-post-content")]//p//text() | '
            '//div[contains(@class, "td-post-content")]//p/strong//text() | '
            '//div[contains(@class, "td-post-content")]//p/em//text() | '
            '//div[@class="td-post-content"]//div[@class="td-paragraph"]//text()'
        ).getall()

        if not content_paragraphs:
            # Fallback: structure alternative
            content_paragraphs = response.xpath(
                '//article//div[contains(@class, "entry-content")]//p//text() | '
                '//div[contains(@class, "tdb-block-inner")]//p//text()'
            ).getall()

        # Nettoyer le contenu
        content = self.clean_article_content(content_paragraphs)

        # Extraire l'image principale
        image_url = (
            response.xpath('//meta[@property="og:image"]/@content').get() or
            response.xpath('//div[@class="td-post-featured-image"]//img/@src').get() or
            response.xpath('//article//img[@class="entry-thumb"]/@src').get() or
            response.xpath('//div[contains(@class, "td-module-image")]//img/@src').get()
        )

        # Extraire la catégorie depuis le badge
        category_badge = response.xpath(
            '//a[@class="td-post-category"]/text()'
        ).get()
        
        category = category_badge if category_badge else response.meta.get('category', '')

        # Extraire les tags
        tags = response.xpath(
            '//ul[@class="td-tags"]//a/text() | '
            '//div[@class="td-post-source-via"]//a/text()'
        ).getall()

        # Préparer les données de l'article
        article_data = {
            'title': title.strip() if title else "",
            'author': author.strip() if author else "AIB",
            'date_publication': publication_date,
            'post': content,
            'url': response.url,
            'image_url': image_url if image_url else "",
            'category': category,
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
                'tweeter',
                'facebook',
                'whatsapp',
                'imprimer',
                'envoyer par email',
                'abonnez-vous',
                'newsletter',
            ]):
                continue
            
            # Ignorer les caractères spéciaux seuls
            if text in ['&nbsp;', '\xa0', '…', '»', '«']:
                continue
            
            cleaned.append(text)
        
        # Joindre avec double saut de ligne
        return '\n\n'.join(cleaned)

    def parse_iso_date(self, date_str):
        """
        Parse les dates ISO 8601 d'AIB Media
        Format: "2025-11-15T15:47:51+01:00"
        Ou texte: "15 novembre 2025"
        """
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        
        try:
            # Format ISO 8601 avec timezone
            if 'T' in date_str:
                # Supprimer le timezone pour simplifier
                date_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
                dt = datetime.fromisoformat(date_clean)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Format texte français: "15 novembre 2025"
            mois_fr = {
                'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
            }
            
            match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_str, re.IGNORECASE)
            if match:
                jour = match.group(1).zfill(2)
                mois_nom = match.group(2).lower()
                annee = match.group(3)
                
                mois = mois_fr.get(mois_nom, '01')
                return f"{annee}-{mois}-{jour} 00:00:00"
            
            return date_str
            
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
    Exécute le scraper AIB Media
    """
    process = CrawlerProcess()
    process.crawl(AIBScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Scraper d\'articles depuis AIB Media (aib.media)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages à scraper par catégorie (défaut: 10)'
    )

    args = parser.parse_args()

    print(f"Démarrage du scraper AIB Media...")
    print(f"Pages max par catégorie: {args.max_pages}")
    print(f"URL de base: https://www.aib.media")
    print(f"Catégories: Dépêches, Événements, Médias, Politique, Économie, etc.")
    print(f"Note: Le site a aussi un sous-domaine regions.aib.media")

    run_scraper(max_pages=args.max_pages)

    print("Scraping terminé!")