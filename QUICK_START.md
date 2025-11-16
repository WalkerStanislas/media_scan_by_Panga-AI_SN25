# MÉDIA-SCAN - Guide de Démarrage Rapide

## Installation

### 1. Créer un environnement virtuel

```bash
python -m venv venv

# Sur macOS/Linux:
source venv/bin/activate

# Sur Windows:
venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt

# Télécharger le modèle français pour spaCy
python -m spacy download fr_core_news_md
```

### 3. Initialiser la base de données

```bash
python -m database.db_manager
```

## Utilisation

### Option 1: Scraper UN média spécifique

```bash
# Lefaso.net (20 pages par rubrique)
python -m scrapers.lefaso_scraper --max-pages 20

# FasoPresse (10 pages par catégorie)
python -m scrapers.fasopresse_scraper --max-pages 10

# Sidwaya (10 pages par catégorie)
python -m scrapers.sidwaya_scraper --max-pages 10

# L'AIB 
python -m scrapers.aib_scraper --max-pages 10

# L'observateur 
python -m scrapers.lobservateur_scraper --max-pages 10

# Burkina 24
python -m scrapers.burkina_24_scraper --max-pages 10

#Collecte training data
python collect_training_data.py --scrapers burkina24  --max-pages 10
```

### Option 2: Utiliser le script principal (RECOMMANDÉ)

```bash
# 1. Scraper TOUS les médias
python main.py --scrape --max-pages 20

# 2. Importer les données dans la base de données
python main.py --import

# 3. Afficher les statistiques
python main.py --stats

# 4. Tout faire en une seule commande
python main.py --all --max-pages 20
```

## Workflow pour le Hackathon

### Jour 1: Collecte de données (MODULE 1)

```bash
# Scraper les médias (objectif: 100+ articles)
python main.py --scrape --max-pages 20

# Importer dans la BDD
python main.py --import

# Vérifier les stats
python main.py --stats
```

**Objectif**: Obtenir au moins 100 articles de 5 médias différents.

### Jour 2: Analyse (MODULES 2, 3, 4, 5)

À développer:
- `analysis/theme_classifier.py` - Classification thématique (MODULE 2)
- `analysis/influence_scorer.py` - Calcul scores d'influence (MODULE 3)
- `analysis/sentiment_detector.py` - Détection contenus sensibles (MODULE 5)

### Jour 3: Dashboard (MODULE 6)

À développer:
- `dashboard/app.py` - Dashboard Streamlit interactif

Lancer avec:
```bash
python main.py --dashboard
```

## Structure des Données

### Articles collectés (JSON)

Emplacement: `data/raw/*.json`

```json
{
  "id": "abc123",
  "media": "Lefaso.net",
  "titre": "Titre de l'article",
  "date": "2025-11-15",
  "url": "https://...",
  "contenu": "Contenu de l'article...",
  "engagement": {
    "likes": 0,
    "partages": 0,
    "commentaires": 5
  },
  "metadata": {
    "rubrique_name": "politique",
    "scraped_at": "2025-11-15T10:30:00"
  },
  "comments": [...]
}
```

### Base de données (SQLite)

Emplacement: `database/media_scan.db`

Tables:
- `medias` - Informations sur les médias
- `articles` - Articles collectés
- `media_stats` - Statistiques quotidiennes
- `alerts` - Alertes de monitoring

## Commandes Utiles

### Vérifier combien d'articles ont été collectés

```bash
python -c "import json; print(len(json.load(open('data/raw/lefaso_articles.json'))))"
```

### Accéder à la base de données

```bash
sqlite3 database/media_scan.db
```

```sql
-- Compter les articles
SELECT COUNT(*) FROM articles;

-- Articles par média
SELECT m.nom, COUNT(a.id) as nb_articles
FROM medias m
LEFT JOIN articles a ON m.id = a.media_id
GROUP BY m.nom;

-- Top médias par engagement
SELECT nom, engagement_total, score_influence, rang
FROM medias
ORDER BY rang;
```

## Conseils pour le Hackathon

1. **Jour 1 (24h)**: Focus sur la collecte
   - Tester chaque scraper individuellement
   - Viser 100+ articles minimum
   - Vérifier la qualité des données

2. **Jour 2 (24h)**: Implémenter l'IA
   - Classification thématique avec CamemBERT
   - Calcul des scores d'influence
   - Bonus: Détection de toxicité

3. **Jour 3 (24h)**: Dashboard et démo
   - Interface Streamlit
   - Visualisations avec Plotly
   - Export PDF/Excel
   - Préparer la démo

## Dépannage

### Erreur lors du scraping

```bash
# Vérifier la connexion internet
ping lefaso.net

# Réduire le nombre de pages
python main.py --scrape --max-pages 5
```

### Base de données verrouillée

```bash
# Supprimer et recréer
rm database/media_scan.db
python -m database.db_manager
```

### Dépendances manquantes

```bash
# Réinstaller toutes les dépendances
pip install -r requirements.txt --upgrade
```

## Support

- Documentation complète: `README.md`
- Configuration: `config/settings.py`
- Logs: Vérifier la console pour les messages d'erreur

Bon courage pour le hackathon! 🚀