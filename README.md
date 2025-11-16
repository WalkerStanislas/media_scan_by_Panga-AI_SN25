# MÉDIA-SCAN
## Système Intelligent d'Observation et d'Analyse des Médias au Burkina Faso

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## Description

MÉDIA-SCAN est une plateforme d'intelligence artificielle développée pour le Conseil Supérieur de la Communication (CSC) du Burkina Faso. Elle permet de collecter automatiquement les contenus des médias burkinabè en ligne, mesurer leur audience et influence, analyser les thèmes traités, et détecter les contenus sensibles.

## Fonctionnalités

### Modules Obligatoires
- **MODULE 1**: Collecte automatique de contenus web (articles, posts)
- **MODULE 2**: Classification thématique par ML (Politique, Économie, Sécurité, Santé, Culture, Sport)
- **MODULE 3**: Calcul des scores d'audience et d'influence
- **MODULE 6**: Dashboard interactif avec visualisations et export de rapports

### Modules Bonus
- **MODULE 4**: Contrôle des grilles de programmes et obligations
- **MODULE 5**: Détection de contenus sensibles (haine, désinformation, toxicité)

## Structure du Projet

```
media-scan/
├── config/                      # Configuration du projet
│   ├── settings.py              # Configuration générale
│   └── label_mapping.py         # Normalisation des labels ML
├── data/                        # Données collectées (général)
│   ├── raw/                     # Données brutes (JSON)
│   └── processed/               # Données traitées
├── train_data/                  # Données d'entraînement ML
│   ├── README.md               # Guide des données training
│   ├── aib_training_data.json
│   ├── lefaso_training_data.json
│   └── merged_training_data.json
├── database/                    # Base de données
│   ├── models.py               # Modèles de données
│   └── db_manager.py           # Gestionnaire de BDD
├── scrapers/                    # Scrapers pour différents médias
│   ├── base_scraper.py         # Classe de base
│   ├── # Scrapers normaux (collecte générale)
│   ├── aib_scraper.py
│   ├── lefaso_scraper.py
│   ├── fasopresse_scraper.py
│   ├── sidwaya_scraper.py
│   ├── lobservateur_scraper.py
│   ├── # Scrapers training (collecte avec labels)
│   ├── aib_training_scraper.py
│   └── lefaso_training_scraper.py
├── analysis/                    # Modules d'analyse
│   ├── theme_classifier.py     # Classification thématique
│   ├── influence_scorer.py     # Calcul scores d'influence
│   └── sentiment_detector.py   # Détection contenus sensibles
├── dashboard/                   # Interface web
│   └── app.py                  # Application Streamlit
├── utils/                       # Utilitaires
│   └── helpers.py
├── main.py                      # Point d'entrée principal
├── collect_training_data.py     # Script de collecte ML
├── TRAINING_DATA_GUIDE.md       # Guide collecte données ML
└── SCRAPERS_COMPARISON.md       # Comparaison scrapers
```

## Installation

### Prérequis
- Python 3.9 ou supérieur
- pip

### Installation des dépendances

```bash
# Créer un environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
# Sur macOS/Linux:
source venv/bin/activate
# Sur Windows:
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Télécharger le modèle français pour spaCy
python -m spacy download fr_core_news_md
```

## Utilisation

### 1. Collecte de données

#### Collecte générale (pour le dashboard et analyses)

```bash
# Scraper pour un média spécifique
python scrapers/aib_scraper.py --max-pages 20
python scrapers/lefaso_scraper.py --max-pages 20

# Scraper tous les médias
python main.py --mode scrape --all
```

#### Collecte pour entraînement du modèle ML

```bash
# Collecter des données avec labels pour l'entraînement
python collect_training_data.py --scrapers aib lefaso --max-pages 10

# Analyser la distribution des labels
python collect_training_data.py --analyze-only

# Fusionner toutes les données d'entraînement
python collect_training_data.py --analyze-only --merge

# Voir le guide complet
# Consultez TRAINING_DATA_GUIDE.md
```

### 2. Analyse des données

```bash
# Classification thématique
python main.py --mode classify

# Calcul des scores d'influence
python main.py --mode analyze
```

### 3. Lancer le dashboard

```bash
streamlit run dashboard/app.py
```

## Médias Supportés

- Lefaso.net
- FasoPresse
- Sidwaya
- L'Observateur Paalga
- AIB (Agence d'Information du Burkina)

## Technologies Utilisées

- **Web Scraping**: Scrapy, BeautifulSoup, Selenium
- **NLP & ML**: Transformers, spaCy, scikit-learn, CamemBERT
- **Data Processing**: pandas, numpy
- **Database**: SQLite, SQLAlchemy
- **Dashboard**: Streamlit, Plotly
- **Content Detection**: Detoxify

## Format des Données

Les données sont stockées au format JSON avec la structure suivante:

```json
{
  "articles": [
    {
      "id": "123",
      "media": "Lefaso.net",
      "titre": "...",
      "date": "2025-11-14",
      "url": "https://...",
      "contenu": "...",
      "categorie": "Politique",
      "engagement": {
        "likes": 45,
        "partages": 12,
        "commentaires": 8
      },
      "sensible": false,
      "toxicite_score": 0.05
    }
  ],
  "medias": [
    {
      "nom": "Lefaso.net",
      "nb_articles": 156,
      "engagement_total": 12450,
      "score_influence": 8.7,
      "rang": 1,
      "actif_90j": true
    }
  ]
}
```

## Développement

### Tests

```bash
# Lancer les tests
python -m pytest tests/
```

### Contribuer

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## Auteurs

Équipe MÉDIA-SCAN - AI Hackathon 2025

## License

Ce projet est sous licence MIT.

## Contact

Pour toute question ou suggestion, contactez le Conseil Supérieur de la Communication (CSC).

---

Développé dans le cadre du Hackathon AI 2025 - MTDPCE
Axe: Gouvernance & Transparence Médiatique