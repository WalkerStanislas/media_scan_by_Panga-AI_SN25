"""
Scraper for Lefaso.net - Burkina Faso news website
Enhanced version with proper structure and data handling
"""
import scrapy
from scrapy.crawler import CrawlerProcess
import sys
from pathlib import Path

# Add parent directory to path to import config
sys.path.append(str(Path(__file__).parent.parent))

from scrapers.base_scraper import BaseMediaScraper
from config.settings import MEDIA_SOURCES, SCRAPING_CONFIG, RAW_DATA_DIR


class LefasoScraper(BaseMediaScraper):
    """
    Scraper for Lefaso.net website
    Collects articles from various rubrics
    """

    name = 'lefaso_scraper'
    media_name = "Lefaso.net"

    def __init__(self, max_pages=20, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_pages = int(max_pages)
        self.config = MEDIA_SOURCES['lefaso']
        self.base_url = self.config['base_url']

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "FEEDS": {
            str(RAW_DATA_DIR / "lefaso_articles.json"): {
                "format": "json",
                "encoding": "utf8",
                "overwrite": False,
            },
        },
        "USER_AGENT": SCRAPING_CONFIG['user_agent'],
        "DOWNLOAD_DELAY": SCRAPING_CONFIG['download_delay'],
        "ROBOTSTXT_OBEY": SCRAPING_CONFIG['robotstxt_obey'],
        "LOG_LEVEL": "INFO",
        "DOWNLOADER_CLIENT_TLS_CIPHERS": "DEFAULT:!DH"
    }

    def start_requests(self):
        """
        Generate requests for all rubrics and pages
        """
        rubrics = self.config['rubrics']

        self.logger.info(f"Starting scraper for {self.media_name}")
        self.logger.info(f"Scraping {len(rubrics)} rubrics, {self.max_pages} pages each")

        for rubric_name, base_url in rubrics.items():
            # Extract rubric ID from URL
            rubrique_id = base_url.split('rubrique')[1].split('&')[0] if 'rubrique' in base_url else rubric_name

            # Scrape multiple pages for each rubric
            for page in range(1, self.max_pages + 1):
                if page == 1:
                    url = base_url
                else:
                    offset = (page - 1) * 20
                    url = f"{base_url}&debut_articles={offset}#pagination_articles"

                self.logger.info(f"Requesting rubric '{rubric_name}' (ID: {rubrique_id}), page {page}")

                yield scrapy.Request(
                    url=url,
                    callback=self.parse_article_list,
                    meta={
                        'rubrique_id': rubrique_id,
                        'rubrique_name': rubric_name,
                        'page_num': page
                    },
                    errback=self.handle_error
                )

    def parse_article_list(self, response):
        """
        Parse the article listing page to extract article URLs
        """
        rubrique_id = response.meta.get('rubrique_id')
        rubrique_name = response.meta.get('rubrique_name')
        page_num = response.meta.get('page_num')

        self.logger.info(f"Parsing rubric '{rubrique_name}' (ID: {rubrique_id}), page {page_num}")

        # Find article blocks
        post_blocks = response.xpath('//div[@class="col-xs-12 col-sm-12 col-md-8 col-lg-8"]')

        # Extract article links
        post_links = post_blocks.xpath('.//a[contains(@href, "spip.php?article")]')
        post_urls = post_links.xpath('@href').getall()

        self.logger.info(f"Found {len(post_urls)} articles on page {page_num} of '{rubrique_name}'")

        # Visit each article
        for url in post_urls:
            absolute_url = response.urljoin(url)
            yield scrapy.Request(
                url=absolute_url,
                callback=self.parse_article,
                meta={
                    'rubrique_id': rubrique_id,
                    'rubrique_name': rubrique_name,
                    'page_num': page_num
                },
                errback=self.handle_error
            )

    def parse_article(self, response):
        """
        Parse individual article page to extract content
        """
        self.logger.info(f"Extracting article: {response.url}")

        rubrique_id = response.meta.get('rubrique_id')
        rubrique_name = response.meta.get('rubrique_name')
        page_num = response.meta.get('page_num')

        # Extract title
        title = response.xpath('//h1[@class="entry-title"]/text()').get()
        if not title:
            title = response.xpath('//h1//text()').get()

        # Extract content
        content_paragraphs = response.xpath('//div[contains(@class, "col-md-8")]//p/text()').getall()
        content = self.clean_text(content_paragraphs)

        # Extract publication date
        date_raw = response.xpath('//div[contains(@class, "article-meta")]//text()').get()
        if not date_raw:
            date_raw = response.xpath('//div[contains(@class, "container")]//p[contains(text(), "Publié")]/text()').get()

        # Parse and format date
        publication_date = self.parse_date(date_raw) if date_raw else ""

        # Extract comments
        comments = self.extract_comments(response)

        # Prepare article data
        article_data = {
            'title': title,
            'date_publication': publication_date,
            'post': content,
            'url': response.url,
            'rubrique_id': rubrique_id,
            'rubrique_name': rubrique_name,
            'page_num': page_num,
            'comments': comments
        }

        # Format and yield article
        formatted_article = self.format_article(article_data)

        self.article_count += 1
        self.logger.info(f"Article extracted successfully. Total articles: {self.article_count}")

        yield formatted_article

    def extract_comments(self, response):
        """
        Extract comments and replies from article
        """
        all_comments = []

        # Find comment blocks
        comments_blocks = response.xpath('//ul[@class="forum"]/li')

        for comment_block in comments_blocks:
            # Main comment
            comment_div = comment_block.xpath('./div[contains(@class, "forum-message")]')

            # Extract comment metadata
            comment_date = comment_div.xpath('.//font/text()').get()

            # Extract comment text
            comment_text_parts = comment_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
            comment_text = self.clean_text(comment_text_parts)

            # Extract replies
            replies_list = []
            replies = comment_block.xpath('./ul/li')

            for reply in replies:
                reply_div = reply.xpath('./div[contains(@class, "forum-message")]')

                reply_date = reply_div.xpath('.//font/text()').get()
                reply_text_parts = reply_div.xpath('.//div[@class="ugccmt-commenttext"]//text()').getall()
                reply_text = self.clean_text(reply_text_parts)

                replies_list.append({
                    'date': reply_date,
                    'text': reply_text
                })

            # Add comment with replies
            all_comments.append({
                'date': comment_date,
                'text': comment_text,
                'replies': replies_list
            })

        return all_comments

    def handle_error(self, failure):
        """
        Handle request errors
        """
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")


def run_scraper(max_pages=20):
    """
    Run the Lefaso scraper
    """
    process = CrawlerProcess(settings={
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
    })

    process.crawl(LefasoScraper, max_pages=max_pages)
    process.start()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Scrape articles from Lefaso.net')
    parser.add_argument('--max-pages', type=int, default=20,
                        help='Maximum number of pages to scrape per rubric (default: 20)')

    args = parser.parse_args()

    print(f"Starting Lefaso.net scraper...")
    print(f"Max pages per rubric: {args.max_pages}")

    run_scraper(max_pages=args.max_pages)

    print("Scraping completed!")