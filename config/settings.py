"""
Configuration settings for MÉDIA-SCAN project
"""
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Database
DATABASE_PATH = BASE_DIR / "database" / "media_scan.db"

# Scraping settings
SCRAPING_CONFIG = {
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "download_delay": 1.0,
    "robotstxt_obey": True,
    "concurrent_requests": 16,
    "retry_times": 3,
}

# Media sources configuration
MEDIA_SOURCES = {
    "lefaso": {
        "name": "Lefaso.net",
        "base_url": "https://lefaso.net",
        "enabled": True,
        "rubrics": {
            "politique": "https://lefaso.net/spip.php?rubrique2",
            "economie": "https://lefaso.net/spip.php?rubrique3",
            "societe": "https://lefaso.net/spip.php?rubrique4",
            "sport": "https://lefaso.net/spip.php?rubrique5",
            "international": "https://lefaso.net/spip.php?rubrique7",
            "culture": "https://lefaso.net/spip.php?rubrique18",
            "diplomatie": "https://lefaso.net/spip.php?rubrique62",
        }
    },
    "fasopresse": {
        "name": "FasoPresse",
        "base_url": "https://fasopresse.net",
        "enabled": True,
    },
    "sidwaya": {
        "name": "Sidwaya",
        "base_url": "https://www.sidwaya.info",
        "enabled": True,
    },
    "observateur_paalga": {
        "name": "L'Observateur Paalga",
        "base_url": "https://www.lobservateur.bf",
        "enabled": True,
    },
    "aib": {
        "name": "AIB (Agence d'Information du Burkina)",
        "base_url": "https://www.aib.media/",
        "enabled": True,
    },
    "burkina_24": {
        "name": "Burkina 24",
        "base_url": "https://burkina24.com",
        "enabled": True,
    }

}

# Theme classification categories
CATEGORIES = [
    "Politique",
    "Économie",
    "Sécurité",
    "Santé",
    "Culture",
    "Sport",
    "International",
    "Société",
    "Autre"
]

# Theme classification keywords (for rule-based approach)
THEME_KEYWORDS = {
    "Politique": ["gouvernement", "président", "ministre", "assemblée", "politique", "élection", "parti", "député"],
    "Économie": ["économie", "budget", "entreprise", "commerce", "croissance", "inflation", "banque", "investissement"],
    "Sécurité": ["sécurité", "armée", "police", "terrorisme", "attaque", "conflit", "militaire", "défense"],
    "Santé": ["santé", "hôpital", "médecin", "maladie", "épidémie", "covid", "vaccin", "soins"],
    "Culture": ["culture", "festival", "musique", "cinéma", "art", "théâtre", "patrimoine"],
    "Sport": ["sport", "football", "basketball", "compétition", "champion", "équipe", "match"],
    "International": ["international", "monde", "pays", "étranger", "diplomatie", "coopération"],
    "Société": ["société", "éducation", "jeunesse", "femme", "enfant", "famille", "social"]
}

# Influence scoring weights
INFLUENCE_WEIGHTS = {
    "volume_publications": 0.20,      # 20% weight for volume
    "engagement_total": 0.35,         # 35% weight for engagement
    "portee_estimee": 0.25,          # 25% weight for reach
    "regularite": 0.10,              # 10% weight for regularity
    "diversite_thematique": 0.10     # 10% weight for thematic diversity
}

# Activity monitoring
ACTIVITY_CONFIG = {
    "min_days_active": 90,           # Minimum days of activity
    "min_articles_per_month": 10,    # Minimum articles per month
    "inactivity_warning_days": 7,    # Days of inactivity before warning
}

# Content detection settings
TOXICITY_THRESHOLD = 0.7             # Threshold for toxic content (0-1)
HATE_SPEECH_THRESHOLD = 0.6          # Threshold for hate speech (0-1)

# ML Model settings
MODEL_CONFIG = {
    "classification_model": "camembert-base",  # French BERT model
    "max_sequence_length": 512,
    "batch_size": 16,
    "test_size": 0.2,
    "random_state": 42,
}

# Dashboard settings
DASHBOARD_CONFIG = {
    "title": "MÉDIA-SCAN - Dashboard CSC",
    "page_icon": ":newspaper:",
    "layout": "wide",
    "default_period_days": 30,
}

# Export settings
EXPORT_CONFIG = {
    "pdf_font": "Arial",
    "excel_sheet_name": "Rapport_Medias",
}

# Logging
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, BASE_DIR / "database"]:
    directory.mkdir(parents=True, exist_ok=True)