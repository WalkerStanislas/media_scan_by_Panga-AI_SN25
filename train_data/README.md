# Données d'Entraînement - MÉDIA SCAN

Ce dossier contient les données d'entraînement collectées pour le modèle de classification d'articles.

## 📋 Structure des Données

Chaque article collecté contient les champs suivants :

```json
{
  "text": "Contenu complet de l'article...",
  "label": "Politique",
  "title": "Titre de l'article",
  "author": "Nom de l'auteur",
  "date": "2025-11-16 00:00:00",
  "url": "https://...",
  "category_raw": "politique",
  "media": "AIB Media",
  "image_url": "https://...",
  "tags": ["tag1", "tag2"],
  "scraped_at": "2025-11-16T10:00:00"
}
```

## 🏷️ Labels Standardisés

Les données sont étiquetées avec les labels suivants :

- **Politique** : Articles sur le gouvernement, élections, partis politiques
- **Économie** : Budget, commerce, entreprises, finance
- **Sécurité** : Armée, police, terrorisme, défense
- **Santé** : Hôpitaux, maladies, épidémies, soins
- **Culture** : Arts, festivals, musique, cinéma, patrimoine
- **Sport** : Football, compétitions, équipes sportives
- **International** : Diplomatie, coopération, actualités mondiales
- **Société** : Éducation, jeunesse, famille, environnement
- **Autre** : Articles ne correspondant à aucune catégorie ci-dessus

## 📊 Fichiers Générés

- `aib_training_data.json` : Données collectées depuis AIB Media
- `lefaso_training_data.json` : Données collectées depuis Lefaso.net
- `merged_training_data.json` : Fusion de toutes les sources (généré avec --merge)

## 🚀 Collecte de Données

### Collecter depuis tous les médias

```bash
python collect_training_data.py --scrapers aib lefaso --max-pages 10
```

### Collecter depuis un média spécifique

```bash
python collect_training_data.py --scrapers aib --max-pages 5
```

### Analyser les données existantes

```bash
python collect_training_data.py --analyze-only
```

### Fusionner toutes les données

```bash
python collect_training_data.py --analyze-only --merge
```

## 📈 Bonnes Pratiques

### 1. Équilibre des Classes

Assurez-vous d'avoir un nombre équilibré d'articles par label pour éviter les biais :

```bash
python collect_training_data.py --analyze-only
```

Cette commande affiche la distribution des labels et le ratio de déséquilibre.

### 2. Diversité des Sources

Collectez depuis plusieurs médias pour avoir une meilleure généralisation :

- AIB Media (moderne, WordPress)
- Lefaso.net (traditionnel, SPIP)
- Autres médias burkinabè

### 3. Volume de Données

Recommandations pour l'entraînement :

- **Minimum** : 100 articles par label (800 total)
- **Recommandé** : 500+ articles par label (4000+ total)
- **Optimal** : 1000+ articles par label (8000+ total)

### 4. Qualité des Données

Avant l'entraînement, vérifiez :

- ✅ Pas d'articles vides (champ `text` non vide)
- ✅ Labels corrects et normalisés
- ✅ Pas de doublons (même URL)
- ✅ Texte de qualité (pas de HTML, pas de navigation)

## 🔧 Configuration Avancée

### Ajouter un nouveau scraper de training

1. Créer `scrapers/[media]_training_scraper.py`
2. Hériter de `BaseMediaScraper`
3. Utiliser `normalize_label()` pour normaliser les catégories
4. Sauvegarder dans `train_data/[media]_training_data.json`

Exemple de structure :

```python
from config.label_mapping import normalize_label

class MonMediaTrainingScraper(BaseMediaScraper):
    custom_settings = {
        "FEEDS": {
            str(TRAIN_DATA_DIR / "monmedia_training_data.json"): {
                "format": "json",
                "encoding": "utf8",
            },
        },
    }

    def parse_article(self, response):
        # ...
        label = normalize_label(category)

        yield {
            'text': content,
            'label': label,
            # ... autres champs
        }
```

### Normalisation des Labels

Le fichier `config/label_mapping.py` contient le mapping des catégories brutes vers les labels standardisés.

Pour ajouter de nouvelles correspondances :

```python
CATEGORY_TO_LABEL = {
    "nouvelle_categorie": "Politique",
    # ...
}
```

## 📝 Exemple d'Utilisation Complète

```bash
# 1. Collecter les données
python collect_training_data.py --scrapers aib lefaso --max-pages 20

# 2. Analyser la distribution
python collect_training_data.py --analyze-only

# 3. Si besoin, ajuster et recollecterr certaines catégories

# 4. Fusionner toutes les données
python collect_training_data.py --analyze-only --merge

# 5. Utiliser merged_training_data.json pour l'entraînement
```

## ⚠️ Notes Importantes

- Les scrapers respectent le `robots.txt` et incluent des délais entre requêtes
- Les données sont sauvegardées en mode "append" (pas d'écrasement)
- Pour recommencer, supprimez les fichiers JSON existants
- Vérifiez toujours la qualité des données avant l'entraînement

## 🎯 Prochaines Étapes

1. Collecter suffisamment de données (min. 100 par label)
2. Nettoyer et valider les données
3. Diviser en ensembles train/validation/test
4. Entraîner le modèle de classification
5. Évaluer les performances sur l'ensemble de test