"""
Scraper for L'Observateur Paalga (lobservateur.bf) - Burkina Faso news website
Site basé sur Joomla avec K2 component - VERSION CORRIGÉE
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import sys
from pathlib import Path
import re
from datetime import datetime
from urllib.parse import urljoin, parse_qs, urlparse

sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseMediaScraper
from config.settings import MEDIA_SOURCES, SCRAPING_CONFIG, RAW_DATA_DIR


class LObservateurScraper(BaseMediaScraper):
    """
    Scraper pour L'Observateur Paalga (lobservateur.bf)
    Site Joomla avec composant K2 - Structure complète
    """

    name = 'lobservateur_scraper'
    media_name = "L'Observateur Paalga"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('lobservateur', {})
        self.base_url = self.config.get('base_url', 'https://www.lobservateur.bf')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "lobservateur_articles.json"): {
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
        Génère les requêtes pour les pages de L'Observateur
        Structure K2: /index.php?option=com_k2&view=itemlist&task=category&id=X&Itemid=Y
        """
        self.logger.info(f"Démarrage du scraper pour {self.media_name}")

        # Catégories principales avec leurs IDs K2
        # Format: (nom, category_id, itemid)
        categories = [
            ('politique', 43, 102),
            ('societe', 23, 112),
            ('arts-culture', 37, 303),
            ('sports', 25, 149),
            ('editorial', 36, 148),
        ]

        for cat_name, cat_id, item_id in categories:
            # Page 1 (sans limitstart)
            yield scrapy.Request(
                url=f"{self.base_url}/index.php?option=com_k2&view=itemlist&layout=category&task=category&id={cat_id}&Itemid={item_id}",
                callback=self.parse_article_list,
                meta={
                    'category': cat_name,
                    'category_id': cat_id,
                    'itemid': item_id,
                    'page_num': 1
                },
                errback=self.handle_error
            )
            
            # Pages suivantes (K2 utilise limitstart)
            # La page affiche 14 articles (2 leading + 6 primary + 6 secondary)
            for page in range(2, self.max_pages + 1):
                limitstart = (page - 1) * 14
                
                yield scrapy.Request(
                    url=f"{self.base_url}/index.php?option=com_k2&view=itemlist&layout=category&task=category&id={cat_id}&Itemid={item_id}&limitstart={limitstart}",
                    callback=self.parse_article_list,
                    meta={
                        'category': cat_name,
                        'category_id': cat_id,
                        'itemid': item_id,
                        'page_num': page
                    },
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse la page de liste d'articles K2
        Structure: <div class="itemList"> contient les articles
        """
        category = response.meta.get('category')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse de {category} - page {page_num}")

        # Extraire les liens depuis toutes les sections K2
        # Section Leading (grands articles en haut)
        leading_links = response.xpath(
            '//div[@id="itemListLeading"]//article//h1/a/@href'
        ).getall()

        # Section Primary (articles moyens)
        primary_links = response.xpath(
            '//div[@id="itemListPrimary"]//article//h1/a/@href'
        ).getall()

        # Section Secondary (petits articles)
        secondary_links = response.xpath(
            '//div[@id="itemListSecondary"]//article//h1/a/@href'
        ).getall()

        # Section Links (liens supplémentaires)
        links_section = response.xpath(
            '//div[@id="itemListLinks"]//li/a/@href'
        ).getall()

        # Combiner tous les liens
        all_links = leading_links + primary_links + secondary_links + links_section

        self.logger.info(f"Trouvé {len(all_links)} articles sur la page {page_num}")
        self.logger.info(f"  Leading: {len(leading_links)}, Primary: {len(primary_links)}, Secondary: {len(secondary_links)}, Links: {len(links_section)}")

        for link in all_links:
            # Construire l'URL complète
            full_url = urljoin(response.url, link)
            
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={'category': category},
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        Structure K2 détaillée de L'Observateur
        """
        self.logger.info(f"Extraction de l'article: {response.url}")

        # Extraire le titre
        # Structure K2: <h2 class="itemTitle"> dans l'article
        title = (
            response.xpath('//h2[@class="itemTitle"]/text()').get() or
            response.xpath('//div[@class="itemHeader"]//h2/text()').get() or
            response.xpath('//meta[@property="og:title"]/@content').get() or
            response.xpath('//title/text()').get()
        )

        # Extraire l'auteur
        # Structure: <li class="itemAuthor"> Écrit par <a>Nom</a>
        author = response.xpath(
            '//li[@class="itemAuthor"]//a[@rel="author"]/text()'
        ).get()
        
        if not author:
            # Fallback: texte brut
            author_text = response.xpath(
                '//li[@class="itemAuthor"]/text()'
            ).get()
            if author_text:
                author = author_text.replace('Écrit par', '').strip()

        # Extraire la date de publication
        # Structure K2: <li class="itemDate"><time datetime="...">texte date</time>
        date_raw = response.xpath(
            '//li[@class="itemDate"]//time/@datetime'
        ).get()
        
        if not date_raw:
            # Fallback: texte de la date
            date_raw = response.xpath(
                '//li[@class="itemDate"]//time/text()'
            ).get()
        
        publication_date = self.parse_date(date_raw) if date_raw else ""

        # Extraire le contenu principal
        # K2 structure: <div class="itemFullText"> pour le texte complet
        # ou <div class="itemIntroText"> pour l'intro
        
        # D'abord essayer le texte complet
        content_html = response.xpath(
            '//div[@class="itemFullText"]'
        ).get()
        
        if content_html:
            # Extraire le texte des paragraphes du texte complet
            content_paragraphs = response.xpath(
                '//div[@class="itemFullText"]//p//text() | '
                '//div[@class="itemFullText"]//p/span//text() | '
                '//div[@class="itemFullText"]//p/b//text() | '
                '//div[@class="itemFullText"]//p/strong//text()'
            ).getall()
        else:
            # Fallback: texte d'introduction
            content_paragraphs = response.xpath(
                '//div[@class="itemIntroText"]//p//text() | '
                '//div[@class="itemIntroText"]//p/span//text() | '
                '//div[@class="itemIntroText"]//p/b//text()'
            ).getall()

        # Nettoyer le contenu
        content = self.clean_article_content(content_paragraphs)

        # Extraire l'image principale
        image_url = (
            response.xpath('//div[@class="itemImageBlock"]//a[@class="itemImage"]/img/@src').get() or
            response.xpath('//div[@class="itemImageBlock"]//img/@src').get() or
            response.xpath('//meta[@property="og:image"]/@content').get()
        )
        
        if image_url:
            image_url = urljoin(response.url, image_url)

        # Extraire la catégorie depuis le breadcrumb K2
        category_from_page = response.xpath(
            '//li[@class="itemCategory"]/a/text()'
        ).get()
        
        category = category_from_page if category_from_page else response.meta.get('category', '')

        # Extraire les tags K2
        tags = response.xpath(
            '//div[@class="itemTagsBlock"]//a/text() | '
            '//ul[@class="itemTags"]//a/text()'
        ).getall()

        # Préparer les données de l'article
        article_data = {
            'title': title.strip() if title else "",
            'author': author.strip() if author else "L'Observateur",
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
            
            # Ignorer le bruit
            if any(skip in text.lower() for skip in [
                'lire aussi',
                'lire la suite',
                'en savoir plus',
                'partager',
                'tweeter',
                'imprimer',
                'envoyer',
                'tags:',
                'catégorie:',
                'écrit par',
                'publié dans',
            ]):
                continue
            
            # Ignorer les espaces non-breaking seuls
            if text.replace('\xa0', '').replace('&nbsp;', '').strip() == '':
                continue
            
            cleaned.append(text)
        
        # Joindre avec double saut de ligne
        return '\n\n'.join(cleaned)

    def parse_date(self, date_str):
        """
        Parse les dates de L'Observateur
        Formats:
        - ISO: "2025-09-30T00:00:00+00:00"
        - Texte: "mardi, 30 septembre 2025 00:00"
        """
        if not date_str:
            return ""
        
        date_str = date_str.strip()
        
        try:
            # Format ISO avec T
            if 'T' in date_str:
                date_clean = re.sub(r'[+-]\d{2}:\d{2}$', '', date_str)
                dt = datetime.fromisoformat(date_clean)
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            
            # Format texte français: "mardi, 30 septembre 2025 00:00"
            mois_fr = {
                'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
                'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
                'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
            }
            
            # Avec jour de la semaine
            match = re.search(
                r'\w+,?\s+(\d{1,2})\s+(\w+)\s+(\d{4})(?:\s+(\d{2}):(\d{2}))?',
                date_str,
                re.IGNORECASE
            )
            
            if match:
                jour = match.group(1).zfill(2)
                mois_nom = match.group(2).lower()
                annee = match.group(3)
                heure = match.group(4) if match.group(4) else "00"
                minute = match.group(5) if match.group(5) else "00"
                
                mois = mois_fr.get(mois_nom, '01')
                return f"{annee}-{mois}-{jour} {heure}:{minute}:00"
            
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
    Exécute le scraper L'Observateur
    """
    process = CrawlerProcess()
    process.crawl(LObservateurScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Scraper d\'articles depuis L\'Observateur Paalga (lobservateur.bf)'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages à scraper par catégorie (défaut: 10)'
    )

    args = parser.parse_args()

    print(f"Démarrage du scraper L'Observateur Paalga...")
    print(f"Pages max par catégorie: {args.max_pages}")
    print(f"URL de base: https://www.lobservateur.bf")
    print(f"Catégories: Politique, Société, Sports, Arts & Culture, Editorial")
    print(f"\nStructure K2 détectée:")
    print(f"  - Leading articles (grands): 2 par page")
    print(f"  - Primary articles (moyens): 6 par page")
    print(f"  - Secondary articles (petits): 6 par page")
    print(f"  - Total: ~14 articles par page")

    run_scraper(max_pages=args.max_pages)

    print("Scraping terminé!")