"""
Base scraper class for all media sources
"""
import scrapy
from datetime import datetime
import hashlib
from typing import Dict, Any


class BaseMediaScraper(scrapy.Spider):
    """
    Base class for all media scrapers
    Provides common functionality for data extraction and storage
    """

    # To be overridden by child classes
    media_name = "Base Media"
    base_url = ""

    custom_settings = {
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7"
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article_count = 0

    def generate_article_id(self, url: str) -> str:
        """
        Generate a unique ID for an article based on its URL
        """
        return hashlib.md5(url.encode()).hexdigest()

    def parse_date(self, date_string: str) -> str:
        """
        Parse date string to standardized format (YYYY-MM-DD)
        Override in child classes if needed
        """
        try:
            # Try common French date formats
            for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]:
                try:
                    dt = datetime.strptime(date_string.strip(), fmt)
                    return dt.strftime("%Y-%m-%d")
                except ValueError:
                    continue

            # If no format matches, return current date
            return datetime.now().strftime("%Y-%m-%d")
        except Exception as e:
            self.logger.warning(f"Error parsing date '{date_string}': {e}")
            return datetime.now().strftime("%Y-%m-%d")

    def clean_text(self, text_list) -> str:
        """
        Clean and join text from list of strings
        """
        if not text_list:
            return ""

        if isinstance(text_list, str):
            return text_list.strip()

        # Join and clean text
        text = ' '.join([t.strip() for t in text_list if t.strip()])
        # Remove multiple spaces
        text = ' '.join(text.split())
        return text

    def calculate_engagement(self, comments: list) -> Dict[str, int]:
        """
        Calculate engagement metrics from comments
        """
        num_comments = len(comments)

        # Count replies
        num_replies = sum(len(comment.get('replies', [])) for comment in comments)

        return {
            "commentaires": num_comments,
            "replies": num_replies,
            "likes": 0,  # To be filled if available
            "partages": 0  # To be filled if available
        }

    def format_article(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format article data to standardized structure
        """
        article_id = self.generate_article_id(data['url'])

        # Calculate engagement
        engagement = self.calculate_engagement(data.get('comments', []))
        if 'likes' in data:
            engagement['likes'] = data['likes']
        if 'partages' in data or 'shares' in data:
            engagement['partages'] = data.get('partages', data.get('shares', 0))

        formatted = {
            "id": article_id,
            "media": self.media_name,
            "titre": data.get('title', ''),
            "date": data.get('date_publication', ''),
            "url": data['url'],
            "contenu": data.get('post', ''),
            "engagement": engagement,
            "article_metadata": {
                "rubrique_id": data.get('rubrique_id'),
                "page_num": data.get('page_num'),
                "scraped_at": datetime.now().isoformat(),
            },
            "comments": data.get('comments', [])
        }

        return formatted

    def start_requests(self):
        """
        To be implemented by child classes
        """
        raise NotImplementedError("start_requests must be implemented by child class")

    def parse(self, response):
        """
        To be implemented by child classes
        """
        raise NotImplementedError("parse must be implemented by child class")