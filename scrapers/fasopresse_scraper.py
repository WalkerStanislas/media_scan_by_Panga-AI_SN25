"""
Scraper for FasoPresse.net - Burkina Faso news website
Version adaptée basée sur l'analyse du HTML du site
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


class FasoPresseScraper(BaseMediaScraper):
    """
    Scraper pour FasoPresse.net
    Le site utilise Joomla 1.5 avec une structure HTML spécifique
    """

    name = 'fasopresse_scraper'
    media_name = "FasoPresse"

    def __init__(self, max_pages=10, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES.get('fasopresse', {})
        self.base_url = self.config.get('base_url', 'https://fasopresse.net')

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "fasopresse_articles.json"): {
                "format": "json",
                "encoding": "utf8",
                "overwrite": False,
            },
        },
        "USER_AGENT": SCRAPING_CONFIG.get('user_agent', 'Mozilla/5.0'),
        "DOWNLOAD_DELAY": SCRAPING_CONFIG.get('download_delay', 2),
        "ROBOTSTXT_OBEY": SCRAPING_CONFIG.get('robotstxt_obey', True),
        "LOG_LEVEL": "INFO",
        "CONCURRENT_REQUESTS": 1,  # Être respectueux avec le serveur
    }

    def start_requests(self):
        """
        Génère les requêtes pour les pages de FasoPresse
        Structure: http://fasopresse.net/[categorie]?start=X
        """
        self.logger.info(f"Démarrage du scraper pour {self.media_name}")

        # Catégories principales du site
        categories = [
            'accueil',
            'politique',
            'economie',
            'societe',
            'sante-et-social',
            'international',
            'sports',
        ]

        for category in categories:
            # Page 1 (pas de paramètre start)
            yield scrapy.Request(
                url=f"{self.base_url}/{category}",
                callback=self.parse_article_list,
                meta={'category': category, 'page_num': 1},
                errback=self.handle_error
            )
            
            # Pages suivantes (avec start=5, 10, 15, etc.)
            # Chaque page affiche 5 articles
            for page in range(2, self.max_pages + 1):
                start_value = (page - 1) * 5
                yield scrapy.Request(
                    url=f"{self.base_url}/{category}?start={start_value}",
                    callback=self.parse_article_list,
                    meta={'category': category, 'page_num': page},
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse la page de liste d'articles
        Structure HTML: <table class="contentpaneopen"> contient les articles
        """
        category = response.meta.get('category')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Analyse de {category} - page {page_num}")

        # Extraire les liens d'articles depuis les titres
        # Structure: <td class="contentheading"><a href="/politique/6151-...">Titre</a>
        article_links = response.xpath(
            '//td[@class="contentheading"]//a[@class="contentpagetitle"]/@href'
        ).getall()

        self.logger.info(f"Trouvé {len(article_links)} articles sur la page {page_num}")

        for link in article_links:
            # Construire l'URL complète
            full_url = response.urljoin(link)
            
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={'category': category},
                errback=self.handle_error
            )

        # Extraire aussi les liens de la section "Plus d'articles..."
        more_articles = response.xpath(
            '//div[@class="blog_more"]//a[@class="blogsection"]/@href'
        ).getall()
        
        for link in more_articles:
            full_url = response.urljoin(link)
            yield scrapy.Request(
                url=full_url,
                callback=self.parse_article,
                meta={'category': category},
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse un article individuel
        Structure HTML spécifique de FasoPresse (Joomla)
        """
        self.logger.info(f"Extraction de l'article: {response.url}")

        # Extraire le titre
        # Structure: <td class="contentheading"><a class="contentpagetitle">Titre</a>
        title = response.xpath(
            '//td[@class="contentheading"]//a[@class="contentpagetitle"]/text()'
        ).get()
        
        if not title:
            title = response.xpath('//h1/text()').get()

        # Extraire l'auteur depuis les métadonnées
        # Structure: <span class="small">Écrit par Sidwaya</span>
        author_meta = response.xpath(
            '//span[@class="small"]/text()'
        ).get()
        if author_meta:
            author_meta = author_meta.replace('Écrit par', '').strip()

        # Extraire la date de publication
        # Structure: <td class="createdate">Vendredi, 29 Juin 2018 09:55</td>
        date_raw = response.xpath(
            '//td[@class="createdate"]/text()'
        ).get()
        
        publication_date = self.parse_french_date(date_raw) if date_raw else ""

        # Extraire la date de mise à jour
        update_date_raw = response.xpath(
            '//td[@class="modifydate"]/text()'
        ).get()
        
        update_date = ""
        if update_date_raw:
            update_date = self.parse_french_date(
                update_date_raw.replace('Mise à jour le', '').strip()
            )

        # Extraire le contenu complet
        # Le contenu principal est dans les <p> de la cellule <td valign="top">
        # qui n'est PAS dans une ligne avec createdate ou modifydate
        
        # Méthode 1: Extraire directement tous les <p> de la zone de contenu
        content_section = response.xpath(
            '//table[@class="contentpaneopen"]//tr[position()>2]//td[@valign="top"]'
        )
        
        if content_section:
            # Extraire tous les textes des paragraphes
            all_text_nodes = content_section.xpath('.//p/text() | .//p/span/text()').getall()
        else:
            # Fallback
            all_text_nodes = response.xpath(
                '//table[@class="contentpaneopen"]//td[@valign="top"]//p/text() | //table[@class="contentpaneopen"]//td[@valign="top"]//p/span/text()'
            ).getall()
        
        # Nettoyer et filtrer le contenu
        content_parts = []
        author_signature = None
        
        for text in all_text_nodes:
            text_clean = text.strip()
            
            # Ignorer les éléments vides ou très courts
            if len(text_clean) < 3:
                continue
                
            # Ignorer les scripts et protections email
            if any(skip in text_clean for skip in [
                'Cette adresse email est protégée',
                'javascript',
                'document.write',
                '<!--',
                '-->'
            ]):
                continue
            
            # Détecter la signature de l'auteur (nom seul sur une ligne)
            # Généralement en fin d'article: "Djakaridia SIRIBIE" ou "Sidwaya"
            if (len(text_clean.split()) <= 3 and 
                text_clean[0].isupper() and 
                not text_clean.endswith('.') and
                len(content_parts) > 0):  # Doit y avoir du contenu avant
                # C'est probablement la signature
                author_signature = text_clean
                continue
            
            content_parts.append(text_clean)
        
        # Joindre le contenu
        content = '\n\n'.join(content_parts)
        
        # Déterminer l'auteur final
        final_author = author_signature if author_signature else (author_meta if author_meta else "")

        # Extraire l'image si présente
        image_url = response.xpath(
            '//table[@class="contentpaneopen"]//td[@valign="top"]//img/@src'
        ).get()
        
        if image_url:
            image_url = response.urljoin(image_url)

        # Préparer les données de l'article
        article_data = {
            'title': title.strip() if title else "",
            'author': final_author,
            'date_publication': publication_date,
            'date_mise_a_jour': update_date,
            'post': content,
            'url': response.url,
            'image_url': image_url if image_url else "",
            'category': response.meta.get('category', ''),
            'comments': [],
            'likes': 0,
            'partages': 0,
        }

        # Formater et retourner
        formatted_article = self.format_article(article_data)
        self.article_count += 1
        
        # Log avec un aperçu du contenu
        content_preview = content[:100] + "..." if len(content) > 100 else content
        self.logger.info(f"Article extrait ({self.article_count}): {title[:50] if title else 'Sans titre'}...")
        self.logger.info(f"Contenu: {len(content)} caractères - Aperçu: {content_preview}")

        yield formatted_article

    def parse_french_date(self, date_str):
        """
        Parse les dates en français du site FasoPresse
        Format: "Vendredi, 29 Juin 2018 09:55"
        """
        if not date_str:
            return ""
        
        # Mapping des mois français vers nombres
        mois_fr = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        
        try:
            # Nettoyer la chaîne
            date_str = date_str.strip()
            
            # Extraire les parties de la date avec regex
            # Format: "Jour, JJ Mois AAAA HH:MM"
            match = re.search(
                r'\w+,?\s+(\d{1,2})\s+(\w+)\s+(\d{4})\s+(\d{2}):(\d{2})',
                date_str,
                re.IGNORECASE
            )
            
            if match:
                jour = match.group(1).zfill(2)
                mois_nom = match.group(2).lower()
                annee = match.group(3)
                heure = match.group(4)
                minute = match.group(5)
                
                mois = mois_fr.get(mois_nom, '01')
                
                # Format ISO: YYYY-MM-DD HH:MM:SS
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
    Exécute le scraper FasoPresse
    """
    process = CrawlerProcess()
    process.crawl(FasoPresseScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Scraper d\'articles depuis FasoPresse.net'
    )
    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages à scraper par catégorie (défaut: 10)'
    )

    args = parser.parse_args()

    print(f"Démarrage du scraper FasoPresse...")
    print(f"Pages max par catégorie: {args.max_pages}")
    print(f"Catégories: accueil, politique, economie, societe, sante-et-social, international, sports")

    run_scraper(max_pages=args.max_pages)

    print("Scraping terminé!")