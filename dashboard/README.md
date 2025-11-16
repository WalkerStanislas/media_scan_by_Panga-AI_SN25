# Dashboard MÉDIA-SCAN

## Description

Dashboard interactif développé avec Streamlit pour l'analyse du paysage médiatique burkinabè. Permet au Conseil Supérieur de la Communication (CSC) de visualiser, analyser et exporter des rapports complets sur l'activité des médias en ligne.

## Fonctionnalités

### 6 Pages Principales

1. **🏠 Accueil** - Vue d'ensemble avec statistiques globales
2. **📊 Analyse des Médias** - Classement et performance des médias
3. **📑 Analyse Thématique** - Distribution et engagement par thématique
4. **⚠️ Contenus Sensibles** - Détection et surveillance des contenus à risque
5. **📈 Engagement** - Métriques d'interaction et d'audience
6. **📥 Export de Rapports** - Génération de rapports PDF/Excel/JSON

### Visualisations Interactives

- Graphiques circulaires (répartition thématique)
- Graphiques en barres (comparaisons)
- Graphiques linéaires (évolutions temporelles)
- Graphiques à bulles (relations multiples)
- Histogrammes (distributions)
- Tableaux dynamiques avec filtres

### Export de Rapports

- **Excel (.xlsx):** 8 onglets avec données détaillées
- **PDF (.pdf):** Rapport synthétique professionnel
- **JSON (.json):** Export brut pour intégrations

## Démarrage Rapide

### Méthode 1: Script Automatique (Recommandé)

**Sur macOS/Linux:**
```bash
./start_dashboard.sh
```

**Sur Windows:**
```batch
start_dashboard.bat
```

### Méthode 2: Commande Manuelle

```bash
# Activer l'environnement virtuel
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Lancer le dashboard
streamlit run dashboard/app.py
```

Le dashboard s'ouvrira automatiquement à l'adresse: **http://localhost:8501**

## Structure des Fichiers

```
dashboard/
├── __init__.py           # Module Python
├── app.py                # Application principale Streamlit
├── data_loader.py        # Chargement et traitement des données
├── report_generator.py   # Génération de rapports
└── README.md            # Ce fichier
```

## Format des Données

Le dashboard attend un fichier JSON dans `data/processed/` avec cette structure:

```json
{
  "articles": [
    {
      "id": "001",
      "media": "Lefaso.net",
      "titre": "Titre de l'article",
      "date": "2025-11-14",
      "url": "https://...",
      "contenu": "Contenu complet...",
      "categorie": "Politique",
      "engagement": {
        "likes": 145,
        "partages": 32,
        "commentaires": 18
      },
      "sensible": false,
      "toxicite_score": 0.02
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

### Catégories Supportées

- Politique
- Économie
- Sécurité
- Santé
- Culture
- Sport
- Autres

## Utilisation avec Données Réelles

1. **Placez votre fichier de données:**
   ```bash
   data/processed/votre_fichier.json
   ```

2. **Option A - Renommer en sample_data.json:**
   ```bash
   mv data/processed/votre_fichier.json data/processed/sample_data.json
   ```

3. **Option B - Modifier le code:**
   Éditez `dashboard/app.py` ligne 54:
   ```python
   loader.load_data("votre_fichier.json")
   ```

4. **Relancer le dashboard:**
   ```bash
   streamlit run dashboard/app.py
   ```

## Fonctionnalités Détaillées

### Page Accueil

**Métriques affichées:**
- Total articles collectés
- Nombre de médias analysés
- Engagement total
- Articles sensibles détectés

**Graphiques:**
- Distribution par catégorie (pie chart)
- Volume par média (bar chart)
- Évolution temporelle (line chart)
- Top 10 articles (liste expandable)

### Page Analyse des Médias

**Tableau de classement:**
- Score d'influence
- Nombre d'articles
- Engagement total
- Statut d'activité (90 jours)

**Visualisations:**
- Score d'influence (bar chart)
- Volume de publications (bar chart)
- Relation volume/engagement (scatter plot)

**Détails par média:**
- Sélection d'un média
- Statistiques détaillées
- Distribution thématique

### Page Analyse Thématique

**Vue d'ensemble:**
- Nombre d'articles par catégorie
- Engagement total par catégorie
- Engagement détaillé (likes, partages, commentaires)

**Analyse détaillée:**
- Sélection d'une catégorie
- Contribution par média
- Articles récents

### Page Contenus Sensibles

**Contrôles:**
- Curseur de seuil de toxicité (0.0 - 1.0)
- Filtres par média
- Filtres par catégorie

**Statistiques:**
- Nombre de contenus sensibles
- Score moyen et maximum
- Distribution par média et catégorie
- Histogramme des scores

**Liste détaillée:**
- Articles classés par toxicité
- Indicateurs visuels (🔴 🟡 🔵)
- Informations complètes

### Page Engagement

**Métriques globales:**
- Total likes, partages, commentaires

**Analyses:**
- Engagement par catégorie (stacked bar)
- Taux d'engagement moyen
- Engagement par média
- Top articles par type d'engagement

### Page Export

**3 formats de rapports:**

1. **Excel:** Complet avec 8 onglets
   - Statistiques globales
   - Classement médias
   - Articles par catégorie/média
   - Engagement détaillé
   - Top articles
   - Contenus sensibles
   - Tous les articles

2. **PDF:** Synthétique et professionnel
   - Vue d'ensemble
   - Classement top 10 médias
   - Distribution thématique
   - Top 10 contenus sensibles
   - Top 10 articles

3. **JSON:** Export brut
   - Toutes les statistiques
   - Format structuré
   - Timestamp de génération

## Architecture Technique

### Technologies

- **Streamlit 1.29.0:** Framework web
- **Plotly 5.18.0:** Graphiques interactifs
- **Pandas 2.1.3:** Traitement données
- **fpdf2 2.7.6:** Génération PDF
- **openpyxl 3.1.2:** Génération Excel

### Modules

1. **app.py:** Interface et navigation
2. **data_loader.py:** Chargement et calculs
3. **report_generator.py:** Export rapports

### Optimisations

- Cache Streamlit pour performances
- Chargement unique au démarrage
- Calculs optimisés avec Pandas
- Visualisations légères avec Plotly

## Personnalisation

### Modifier les Couleurs

Éditez le CSS dans `app.py` (lignes 27-39):
```python
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    ...
    </style>
    """, unsafe_allow_html=True)
```

### Ajouter une Page

1. Ajoutez l'option dans la sidebar:
```python
page = st.sidebar.radio(
    "Navigation",
    ["Page 1", "Page 2", "Nouvelle Page"]
)
```

2. Créez la section:
```python
elif page == "Nouvelle Page":
    st.title("Nouvelle Page")
    # Votre contenu ici
```

### Modifier les Thèmes Plotly

Changez `color_discrete_sequence` ou `color_continuous_scale`:
```python
fig = px.bar(..., color_continuous_scale='Viridis')
# Options: 'Viridis', 'Blues', 'Reds', 'Greens', etc.
```

## Dépannage

### Le dashboard ne démarre pas

```bash
# Vérifier les dépendances
pip install -r requirements.txt

# Vérifier Python
python --version  # Doit être 3.9+

# Vérifier Streamlit
streamlit --version
```

### Erreur de fichier non trouvé

```bash
# Vérifier la présence du fichier
ls -la data/processed/

# Créer le répertoire si nécessaire
mkdir -p data/processed
```

### Problème d'export PDF

```bash
# Réinstaller fpdf2
pip install --upgrade fpdf2
```

### Problème d'export Excel

```bash
# Réinstaller openpyxl
pip install --upgrade openpyxl
```

### Port 8501 déjà utilisé

```bash
# Spécifier un autre port
streamlit run dashboard/app.py --server.port 8502
```

## Performance

### Temps de Chargement

- Petit dataset (<100 articles): <1 seconde
- Moyen dataset (100-1000 articles): 1-3 secondes
- Grand dataset (>1000 articles): 3-5 secondes

### Optimisations

- Utilisation du cache Streamlit
- Calculs groupés avec Pandas
- Chargement paresseux des graphiques
- Pagination automatique des listes

## Tests

### Données Exemple

Un fichier `sample_data.json` est fourni avec:
- 20 articles exemple
- 5 médias
- Toutes les catégories
- Exemples de contenus sensibles

### Tester le Dashboard

```bash
# Avec les données exemple
streamlit run dashboard/app.py

# Vérifier toutes les pages
# Tester les filtres
# Générer les rapports
```

## Documentation Complète

Consultez le guide complet: **DASHBOARD_GUIDE.md**

## Support

Pour toute question:
- Consultez le guide utilisateur
- Vérifiez la documentation du projet
- Contactez l'équipe de développement

## Licence

MIT License - Développé pour le CSC Burkina Faso

## Crédits

**Développé dans le cadre du Hackathon AI 2025**
- Partenaire: MTDPCE
- Client: Conseil Supérieur de la Communication (CSC)
- Axe: Gouvernance & Transparence Médiatique

---

**Version:** 1.0
**Dernière mise à jour:** Novembre 2025