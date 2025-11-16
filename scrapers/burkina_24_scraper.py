"""
Scraper for Burkina24 (burkina24.com) - Burkina Faso news website
Site WordPress avec thème Jannah (TieLabs)
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import sys
from pathlib import Path
import re
from datetime import datetime, timedelta

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseMediaScraper
from config.settings import MEDIA_SOURCES, SCRAPING_CONFIG, RAW_DATA_DIR


class Burkina24Scraper(BaseMediaScraper):
    """
    Scraper pour Burkina24
    Site WordPress moderne avec thème Jannah
    """

    name = 'burkina24_scraper'
    media_name = "Burkina24"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('burkina24', {})
        self.base_url = self.config.get('base_url', 'https://burkina24.com')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "burkina24_articles.json"): {
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
        Génère les requêtes pour les pages de Burkina24
        Structure: https://burkina24.com/category/[categorie]/page/X/
        """
        self.logger.info(f"Démarrage du scraper pour {self.media_name}")

        # Catégories principales du site (structure hiérarchique)
        categories = [
            'actualite/societe/sante',
            'actualite/societe/societe-societe',
            'actualite/education',
            'actualite/politique',
            'actualite/economie',
            'actualite/sports',
            'actualite/culture',
            'actualite/securite',
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
        Structure Jannah: <li class="post-item"> contient les articles
        """
        category = response.meta.get('category')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse de {category} - page {page_num}")

        # Extraire les liens d'articles depuis les éléments post-item
        # Structure: <h2 class="post-title"><a href="URL">
        article_links = response.xpath(
            '//li[contains(@class, "post-item")]//h2[@class="post-title"]/a/@href'
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
        Structure WordPress/Jannah de Burkina24
        """
        self.logger.info(f"Extraction de l'article: {response.url}")

        # Extraire le titre
        title = (
            response.xpath('//h1[@class="post-title entry-title"]//text()').get() or
            response.xpath('//h1[contains(@class, "entry-title")]//text()').get() or
            response.xpath('//meta[@property="og:title"]/@content').get() or
            response.xpath('//title/text()').get()
        )

        # Extraire l'auteur
        # Structure Jannah: <span class="meta-author"><a>Nom</a>
        author = response.xpath(
            '//span[@class="meta-author"]//a[@class="author-name tie-icon"]/@title | '
            '//span[@class="meta-author"]//a[@class="author-name tie-icon"]/text() | '
            '//a[@rel="author"]/text()'
        ).get()
        
        if not author:
            author = response.xpath('//meta[@name="author"]/@content').get()

        # Extraire la date de publication
        # Burkina24 utilise des dates relatives: "il y a X heures/jours"
        date_raw = response.xpath(
            '//span[contains(@class, "date")][@class="meta-item tie-icon"]/text() | '
            '//time[@class="entry-date published"]/@datetime | '
            '//meta[@property="article:published_time"]/@content'
        ).get()
        
        publication_date = self.parse_relative_date(date_raw) if date_raw else ""

        # Extraire le contenu principal
        # Jannah structure: <div class="entry-content entry-content-single">
        content_paragraphs = response.xpath(
            '//div[contains(@class, "entry-content")]//p//text() | '
            '//div[contains(@class, "entry-content")]//p/strong//text() | '
            '//div[contains(@class, "entry-content")]//p/em//text() | '
            '//div[contains(@class, "entry-content")]//p/span//text()'
        ).getall()

        if not content_paragraphs:
            # Fallback
            content_paragraphs = response.xpath(
                '//article//div[@class="entry-content"]//p//text()'
            ).getall()

        # Nettoyer le contenu
        content = self.clean_article_content(content_paragraphs)

        # Extraire l'image principale
        image_url = (
            response.xpath('//meta[@property="og:image"]/@content').get() or
            response.xpath('//div[@class="featured-image-area"]//img/@src').get() or
            response.xpath('//article//img[@class="attachment-jannah-image-post size-jannah-image-post wp-post-image"]/@src').get()
        )

        # Extraire les catégories depuis les meta ou breadcrumb
        categories = response.xpath(
            '//span[@class="post-cat-wrap"]//a/text() | '
            '//div[@class="post-categories"]//a/text()'
        ).getall()
        
        # Utiliser la première catégorie ou celle du meta
        category = categories[0] if categories else response.meta.get('category', '')

        # Extraire les tags
        tags = response.xpath(
            '//div[@class="post-tags"]//a/text() | '
            '//span[@class="tags-links"]//a/text()'
        ).getall()

        # Préparer les données de l'article
        article_data = {
            'title': title.strip() if title else "",
            'author': author.strip() if author else "Burkina24",
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
                'lire aussi',
                'lire la suite',
                'voir aussi',
                'partager',
                'tweeter',
                'facebook',
                'whatsapp',
                'imprimer',
                's\'abonner',
                'newsletter',
                'commentaires',
                'dernière actualité',
            ]):
                continue
            
            # Ignorer les espaces spéciaux
            if text.replace('\xa0', '').replace('&nbsp;', '').strip() == '':
                continue
            
            cleaned.append(text)
        
        # Joindre avec double saut de ligne
        return '\n\n'.join(cleaned)

    def parse_relative_date(self, date_str):
        """
        Parse les dates relatives de Burkina24
        Formats:
        - "il y a 40 minutes"
        - "il y a 19 heures"
        - "il y a 2 jours"
        - "il y a 1 semaine"
        - ISO: "2025-11-16T..."
        """
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        
        try:
            # Format ISO direct
            if 'T' in date_str or re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                date_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
                dt = datetime.fromisoformat(date_clean)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Format relatif français
            now = datetime.now()
            
            # "il y a X minutes"
            match = re.search(r'il y a (\d+) minute', date_str, re.IGNORECASE)
            if match:
                minutes = int(match.group(1))
                dt = now - timedelta(minutes=minutes)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # "il y a X heures"
            match = re.search(r'il y a (\d+) heure', date_str, re.IGNORECASE)
            if match:
                hours = int(match.group(1))
                dt = now - timedelta(hours=hours)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # "il y a X jours"
            match = re.search(r'il y a (\d+) jour', date_str, re.IGNORECASE)
            if match:
                days = int(match.group(1))
                dt = now - timedelta(days=days)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # "il y a X semaines"
            match = re.search(r'il y a (\d+) semaine', date_str, re.IGNORECASE)
            if match:
                weeks = int(match.group(1))
                dt = now - timedelta(weeks=weeks)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # "il y a X mois"
            match = re.search(r'il y a (\d+) mois', date_str, re.IGNORECASE)
            if match:
                months = int(match.group(1))
                dt = now - timedelta(days=months * 30)  # Approximation
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
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
    Exécute le scraper Burkina24
    """
    process = CrawlerProcess()
    process.crawl(Burkina24Scraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Scraper d\'articles depuis Burkina24 (burkina24.com)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages à scraper par catégorie (défaut: 10)'
    )

    args = parser.parse_args()

    print(f"Démarrage du scraper Burkina24...")
    print(f"Pages max par catégorie: {args.max_pages}")
    print(f"URL de base: https://burkina24.com")
    print(f"Catégories: Santé, Société, Education, Politique, Economie, Sports, etc.")
    print(f"\nParticularités:")
    print(f"  - Thème Jannah (moderne)")
    print(f"  - Dates relatives ('il y a X heures')")
    print(f"  - Structure hiérarchique des catégories")

    run_scraper(max_pages=args.max_pages)

    print("Scraping terminé!")