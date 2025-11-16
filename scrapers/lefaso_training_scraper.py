"""
Training Scraper for Lefaso.net
Collecte des données avec labels pour l'entraînement du modèle de classification
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

# Répertoire pour les données d'entraînement
TRAIN_DATA_DIR = Path(__file__).parent.parent / "train_data"
TRAIN_DATA_DIR.mkdir(parents=True, exist_ok=True)


class LefasoTrainingScraper(BaseMediaScraper):
    """
    Training scraper pour Lefaso.net avec labels normalisés
    """

    name = 'lefaso_training_scraper'
    media_name = "Lefaso.net"

    def __init__(self, max_pages=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES['lefaso']
        self.base_url = self.config['base_url']

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(TRAIN_DATA_DIR / "lefaso_training_data.json"): {
                "format": "json",
                "encoding": "utf8",
                "overwrite": False,
            },
        },
        "USER_AGENT": SCRAPING_CONFIG['user_agent'],
        "DOWNLOAD_DELAY": SCRAPING_CONFIG['download_delay'],
        "ROBOTSTXT_OBEY": SCRAPING_CONFIG['robotstxt_obey'],
        "LOG_LEVEL": "INFO",
        "DOWNLOADER_CLIENT_TLS_CIPHERS": "DEFAULT:!DH",
        "CONCURRENT_REQUESTS": 2,
    }

    def start_requests(self):
        """
        Génère les requêtes pour les rubriques avec labels
        """
        rubrics = self.config['rubrics']

        self.logger.info(f"Démarrage du training scraper pour {self.media_name}")
        self.logger.info(f"Collecte de {len(rubrics)} rubriques, {self.max_pages} pages chacune")

        for rubric_name, base_url in rubrics.items():
            # Extraire l'ID de rubrique
            rubrique_id = base_url.split('rubrique')[1].split('&')[0] if 'rubrique' in base_url else rubric_name

            # Normaliser le label
            label = normalize_label(rubric_name)

            # Scraper plusieurs pages
            for page in range(1, self.max_pages + 1):
                if page == 1:
                    url = base_url
                else:
                    offset = (page - 1) * 20
                    url = f"{base_url}&debut_articles={offset}#pagination_articles"

                self.logger.info(f"Requête rubrique '{rubric_name}' (Label: {label}), page {page}")

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article_list,
                    meta={
                        'rubrique_id': rubrique_id,
                        'rubrique_name': rubric_name,
                        'label': label,
                        'page_num': page
                    },
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse la liste d'articles
        """
        rubrique_id = response.meta.get('rubrique_id')
        rubrique_name = response.meta.get('rubrique_name')
        label = response.meta.get('label')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse rubrique '{rubrique_name}' (Label: {label}), page {page_num}")

        # Trouver les blocs d'articles
        post_blocks = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')

        # Extraire les liens
        post_links = post_blocks.xpath('.//a[contains(@href, "spip.php?article")]')
        post_urls = post_links.xpath('@href').getall()

        self.logger.info(f"Trouvé {len(post_urls)} articles")

        # Dédupliquer
        unique_urls = list(dict.fromkeys(post_urls))

        for url in unique_urls:
            # Construire l'URL complète
            full_url = response.urljoin(url)

            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={
                    'rubrique_id': rubrique_id,
                    'rubrique_name': rubrique_name,
                    'label': label,
                    'page_num': page_num
                },
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        """
        self.logger.info(f"Extraction article: {response.url}")

        rubrique_name = response.meta.get('rubrique_name')
        label = response.meta.get('label')

        # Extraire le titre
        title = response.xpath('//h1[@class="spip"]/text()').get()
        if not title:
            title = response.xpath('//title/text()').get()

        # Extraire l'auteur
        author = response.xpath('//span[@class="auteur"]/text()').get()
        if not author:
            author = response.xpath('//div[@class="auteur"]//text()').get()

        # Extraire la date
        date_raw = response.xpath('//p[@class="info-publi"]//text()').getall()
        date_text = ' '.join([d.strip() for d in date_raw if d.strip()])

        # Parser la date
        publication_date = self.parse_date_text(date_text)

        # Extraire le contenu
        #content_paras = response.xpath('//div[@class="texte"]//p//text()').getall()
        content_paras = response.xpath('//div[contains(@class, "col-md-8")]//p/text()').getall()
        if not content_paras:
            content_paras = response.xpath('//div[@class="chapo"]//text() | //div[@class="texte"]//text()').getall()

        content = self.clean_content(content_paras)

        # Extraire l'image
        image_url = response.xpath('//div[@class="spip_documents"]//img/@src').get()
        if image_url:
            image_url = response.urljoin(image_url)

        # Extraire les tags/mots-clés
        tags = response.xpath('//div[@class="tags"]//a/text()').getall()

        # Préparer les données d'entraînement
        training_data = {
            'text': content,
            'label': label,
            'title': title.strip() if title else "",
            'author': author.strip() if author else "Lefaso",
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
        self.logger.info(f"Contenu: {len(content)} caractères")

        yield training_data

    def clean_content(self, paragraphs):
        """
        Nettoie le contenu
        """
        cleaned = []

        for para in paragraphs:
            text = para.strip()

            if len(text) < 3:
                continue

            # Ignorer éléments de navigation
            if any(skip in text.lower() for skip in [
                'lire aussi', 'voir aussi', 'partager', 'imprimer',
                'envoyer', 'commentaire', 'réagir'
            ]):
                continue

            cleaned.append(text)

        return '\n\n'.join(cleaned)

    def parse_date_text(self, date_text):
        """
        Parse le texte de date de Lefaso
        Format: "publié le lundi 15 novembre 2025"
        """
        if not date_text:
            return ""

        try:
            mois_fr = {
                'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
            }

            # Pattern: jour mois année
            match = re.search(r'(\d{1,2})\s+(\w+)\s+(\d{4})', date_text, re.IGNORECASE)
            if match:
                jour = match.group(1).zfill(2)
                mois_nom = match.group(2).lower()
                annee = match.group(3)

                mois = mois_fr.get(mois_nom, '01')
                return f"{annee}-{mois}-{jour} 00:00:00"

            return ""

        except Exception as e:
            self.logger.warning(f"Erreur parsing date '{date_text}': {e}")
            return ""

    def handle_error(self, failure):
        """
        Gestion des erreurs
        """
        self.logger.error(f"Échec: {failure.request.url}")
        self.logger.error(f"Raison: {failure.value}")


def run_scraper(max_pages=20):
    """
    Exécute le training scraper
    """
    process = CrawlerProcess()
    process.crawl(LefasoTrainingScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Training scraper pour Lefaso.net avec labels normalisés'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=20,
        help='Nombre maximum de pages par rubrique (défaut: 20)'
    )

    args = parser.parse_args()

    print(f"Démarrage du training scraper Lefaso.net...")
    print(f"Pages max par rubrique: {args.max_pages}")
    print(f"Sortie: train_data/lefaso_training_data.json")
    print(f"Labels normalisés automatiquement")

    run_scraper(max_pages=args.max_pages)

    print("Training scraping terminé!")