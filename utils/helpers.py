"""
Utility functions for MÉDIA-SCAN project
"""
import re
import json
from datetime import datetime
from typing import List, Dict
from pathlib import Path


def clean_text(text: str) -> str:
    """
    Clean text by removing extra whitespace and special characters
    """
    if not text:
        return ""

    # Remove extra whitespace
    text = ' '.join(text.split())

    # Remove special characters but keep accented characters
    text = re.sub(r'[^\w\s\-.,!?;:àâäéèêëïîôùûüÿçÀÂÄÉÈÊËÏÎÔÙÛÜŸÇ]', '', text)

    return text.strip()


def parse_french_date(date_string: str) -> str:
    """
    Parse French date formats to YYYY-MM-DD
    """
    if not date_string:
        return datetime.now().strftime("%Y-%m-%d")

    # Common French month names
    french_months = {
        'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
        'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
        'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
    }

    # Try to extract date components
    for month_name, month_num in french_months.items():
        if month_name in date_string.lower():
            # Extract day and year
            numbers = re.findall(r'\d+', date_string)
            if len(numbers) >= 2:
                day = numbers[0].zfill(2)
                year = numbers[1] if len(numbers[1]) == 4 else '20' + numbers[1]
                return f"{year}-{month_num}-{day}"

    # Try standard formats
    date_formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d %B %Y",
        "%Y-%m-%dT%H:%M:%S"
    ]

    for fmt in date_formats:
        try:
            dt = datetime.strptime(date_string.strip(), fmt)
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            continue

    # If all fails, return current date
    return datetime.now().strftime("%Y-%m-%d")


def load_json_file(file_path: Path) -> List[Dict]:
    """
    Load articles from JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            return [data]
        return data
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []


def save_json_file(data: List[Dict], file_path: Path):
    """
    Save data to JSON file
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Data saved to {file_path}")
    except Exception as e:
        print(f"Error saving to {file_path}: {e}")


def calculate_engagement_score(likes: int, shares: int, comments: int) -> float:
    """
    Calculate engagement score with weighted metrics
    """
    # Weighted engagement: shares > comments > likes
    score = (likes * 1.0) + (comments * 2.0) + (shares * 3.0)
    return score


def normalize_score(value: float, min_val: float, max_val: float, scale: int = 10) -> float:
    """
    Normalize a value to a scale (default 0-10)
    """
    if max_val == min_val:
        return scale / 2

    normalized = ((value - min_val) / (max_val - min_val)) * scale
    return round(normalized, 2)


def extract_keywords(text: str, n: int = 10) -> List[str]:
    """
    Extract top N keywords from text (simple frequency-based)
    """
    if not text:
        return []

    # French stop words
    stop_words = {
        'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'est',
        'dans', 'pour', 'que', 'qui', 'par', 'sur', 'avec', 'ce', 'cette',
        'sont', 'au', 'aux', 'son', 'sa', 'ses', 'a', 'à', 'ont', 'été',
        'plus', 'comme', 'mais', 'ou', 'où', 'donc', 'or', 'ni', 'car'
    }

    # Tokenize and clean
    words = re.findall(r'\b[a-zàâäéèêëïîôùûüÿç]{3,}\b', text.lower())

    # Filter stop words and count
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Get top N
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, _ in sorted_words[:n]]


def format_number(num: int) -> str:
    """
    Format large numbers with K, M suffix
    """
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return str(num)


def get_date_range_filter(days: int) -> str:
    """
    Get date string for N days ago
    """
    from datetime import timedelta
    date = datetime.now() - timedelta(days=days)
    return date.strftime("%Y-%m-%d")


def export_to_csv(data: List[Dict], file_path: Path, columns: List[str] = None):
    """
    Export data to CSV file
    """
    import csv

    if not data:
        print("No data to export")
        return

    try:
        # Use specified columns or all keys from first item
        if columns is None:
            columns = list(data[0].keys())

        with open(file_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()

            for row in data:
                # Only write specified columns
                filtered_row = {k: v for k, v in row.items() if k in columns}
                writer.writerow(filtered_row)

        print(f"Data exported to {file_path}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")