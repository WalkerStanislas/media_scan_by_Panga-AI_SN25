"""
Training Scraper for Sidwaya.info
Collecte des donn�es avec labels pour l'entra�nement du mod�le de classification
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import sys
from pathlib import Path
import re
from datetime import datetime

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseMediaScraper
from config.settings import MEDIA_SOURCES, SCRAPING_CONFIG
from config.label_mapping import normalize_label

# R�pertoire pour les donn�es d'entra�nement
TRAIN_DATA_DIR = Path(__file__).parent.parent / "train_data"
TRAIN_DATA_DIR.mkdir(parents=True, exist_ok=True)


class SidwayaTrainingScraper(BaseMediaScraper):
    """
    Training scraper pour Sidwaya.info avec labels normalis�s
    """

    name = 'sidwaya_training_scraper'
    media_name = "Sidwaya"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('sidwaya', {})
        self.base_url = self.config.get('base_url', 'https://www.sidwaya.info')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(TRAIN_DATA_DIR / "sidwaya_training_data.json"): {
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
        G�n�re les requ�tes pour les pages de Sidwaya
        Structure: https://www.sidwaya.info/bfcategories/[categorie]/page/X/
        """
        self.logger.info(f"Démarrage du training scraper pour {self.media_name}")

        # Cat�gories principales avec mapping vers labels
        # Note sp�ciale: "nouvelle-du-front" est mapp� vers "S�curit�"
        categories = {
            'nouvelle-du-front': 'Sécurité',
            #'politique': 'Politique',
            #'economie': 'Economie',
            #'societe': 'Société',
            'sport': 'Sport',
            #'culture': 'Culture',
            'sante': 'Santé',
            #'international/diplomatie': 'International',
            #'international/politique-international': 'International',
        }

        self.logger.info(f"Collecte de {len(categories)} catégories, {self.max_pages} pages chacune")

        for category, rubric_name in categories.items():
            # Normaliser le label
            label = normalize_label(rubric_name)

            self.logger.info(f"Configuration catégorie '{category}' -> Label: {label}")

            # Page 1 (sans /page/)
            yield scrapy.Request(
                url=f"{self.base_url}/bfcategories/{category}/",
                callback=self.parse_article_list,
                meta={
                    'category': category,
                    'rubrique_name': rubric_name,
                    'label': label,
                    'page_num': 1
                },
                errback=self.handle_error
            )

            # Pages suivantes
            for page in range(2, self.max_pages + 1):
                yield scrapy.Request(
                    url=f"{self.base_url}/bfcategories/{category}/page/{page}/",
                    callback=self.parse_article_list,
                    meta={
                        'category': category,
                        'rubrique_name': rubric_name,
                        'label': label,
                        'page_num': page
                    },
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse la page de liste d'articles
        Structure: <div class="td_module_1"> contient les articles
        """
        category = response.meta.get('category')
        rubrique_name = response.meta.get('rubrique_name')
        label = response.meta.get('label')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse rubrique '{rubrique_name}' (Label: {label}), page {page_num}")

        # Extraire les liens d'articles
        # Structure: <h3 class="entry-title td-module-title"><a href="URL">
        article_links = response.xpath(
            '//h3[contains(@class, "entry-title") and contains(@class, "td-module-title")]//a/@href'
        ).getall()

        self.logger.info(f"Trouv� {len(article_links)} articles sur la page {page_num}")

        for link in article_links:
            yield scrapy.Request(
                url=link,
                callback=self.parse_article,
                meta={
                    'category': category,
                    'rubrique_name': rubrique_name,
                    'label': label,
                    'page_num': page_num
                },
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        Structure WordPress/tagDiv de Sidwaya
        """
        self.logger.info(f"Extraction article: {response.url}")

        rubrique_name = response.meta.get('rubrique_name')
        label = response.meta.get('label')

        # Extraire le titre
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
        content = self.clean_content(content_paragraphs)

        # Extraire l'image principale
        image_url = (
            response.xpath('//meta[@property="og:image"]/@content').get() or
            response.xpath('//article//img[@class="entry-thumb"]/@src').get() or
            response.xpath('//div[contains(@class, "td-post-featured-image")]//img/@src').get()
        )

        # Extraire les tags/cat�gories
        tags = response.xpath(
            '//ul[@class="td-tags"]//a/text()'
        ).getall()

        # Pr�parer les donn�es d'entra�nement
        training_data = {
            'text': content,
            'label': label,
            'title': title.strip() if title else "",
            'author': author.strip() if author else "Sidwaya",
            'date': publication_date,
            'url': response.url,
            'category_raw': rubrique_name,
            'media': self.media_name,
            'image_url': image_url if image_url else "",
            'tags': tags,
            'scraped_at': datetime.now().isoformat(),
        }

        self.article_count += 1

        self.logger.info(
            f"Article extrait ({self.article_count}): "
            f"Label={label}, Titre={title[:50] if title else 'Sans titre'}..."
        )
        self.logger.info(f"Contenu: {len(content)} caract�res")

        yield training_data

    def clean_content(self, paragraphs):
        """
        Nettoie le contenu de l'article
        """
        cleaned = []

        for para in paragraphs:
            text = para.strip()

            # Ignorer les textes vides ou tr�s courts
            if len(text) < 3:
                continue

            # Ignorer les �l�ments de navigation/UI
            if any(skip in text.lower() for skip in [
                'cliquez ici',
                'lire aussi',
                'voir aussi',
                'partager',
                'tweet',
                'facebook',
                'whatsapp',
                'imprimer',
                'envoyer',
                'commentaire',
                'r�agir'
            ]):
                continue

            cleaned.append(text)

        # Joindre avec double saut de ligne pour s�parer les paragraphes
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
        Gestion des erreurs de requ�te
        """
        self.logger.error(f"�chec de la requ�te: {failure.request.url}")
        self.logger.error(f"Raison: {failure.value}")


def run_scraper(max_pages=10):
    """
    Ex�cute le training scraper
    """
    process = CrawlerProcess()
    process.crawl(SidwayaTrainingScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Training scraper pour Sidwaya.info avec labels normalis�s'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages par cat�gorie (d�faut: 10)'
    )

    args = parser.parse_args()

    print(f"D�marrage du training scraper Sidwaya.info...")
    print(f"Pages max par cat�gorie: {args.max_pages}")
    print(f"Sortie: train_data/sidwaya_training_data.json")
    print(f"Labels normalis�s automatiquement")
    print(f"Note: 'nouvelle-du-front' -> Label 'S�curit�'")

    run_scraper(max_pages=args.max_pages)

    print("Training scraping termin�!")