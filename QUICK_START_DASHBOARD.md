# Démarrage Rapide du Dashboard MÉDIA-SCAN

## 🚀 Lancement en 3 Étapes

### Étape 1: Préparer l'Environnement
```bash
# Activer l'environnement virtuel
source venv/bin/activate  # macOS/Linux
# OU
venv\Scripts\activate     # Windows
```

### Étape 2: Lancer le Dashboard
```bash
# Méthode rapide (recommandée)
./start_dashboard.sh      # macOS/Linux
# OU
start_dashboard.bat       # Windows

# Méthode manuelle
streamlit run dashboard/app.py
```

### Étape 3: Accéder au Dashboard
Le dashboard s'ouvre automatiquement dans votre navigateur à:
**http://localhost:8501**

## 📊 Fonctionnalités Disponibles

### 6 Pages d'Analyse

1. **🏠 Accueil**
   - Vue d'ensemble du paysage médiatique
   - Statistiques globales
   - Top articles

2. **📊 Analyse des Médias**
   - Classement par influence
   - Détails par média
   - Comparaisons

3. **📑 Analyse Thématique**
   - Distribution par catégorie
   - Engagement par thème
   - Articles récents

4. **⚠️ Contenus Sensibles**
   - Détection automatique
   - Filtres interactifs
   - Scores de toxicité

5. **📈 Engagement**
   - Likes, partages, commentaires
   - Top articles par métrique
   - Tendances

6. **📥 Export de Rapports**
   - PDF professionnel
   - Excel détaillé (8 onglets)
   - JSON pour intégrations

## 📁 Structure des Données

Le dashboard attend un fichier JSON dans `data/processed/`:

```json
{
  "articles": [...],
  "medias": [...]
}
```

**Fichier actuel:** `sample_data.json` (20 articles exemple)

## 🔄 Utiliser vos Propres Données

### Option 1: Renommer votre fichier
```bash
mv data/processed/vos_donnees.json data/processed/sample_data.json
```

### Option 2: Modifier le code
Éditez `dashboard/app.py` ligne 54:
```python
loader.load_data("vos_donnees.json")
```

Puis relancez:
```bash
streamlit run dashboard/app.py
```

## 🛠️ Commandes Utiles

### Recharger les Données
Cliquez sur "🔄 Recharger les données" dans la sidebar du dashboard

### Arrêter le Dashboard
Appuyez sur `Ctrl+C` dans le terminal

### Changer de Port
```bash
streamlit run dashboard/app.py --server.port 8502
```

## 📚 Documentation Complète

- **DASHBOARD_GUIDE.md** - Guide utilisateur complet
- **dashboard/README.md** - Documentation technique
- **DASHBOARD_IMPLEMENTATION.md** - Détails d'implémentation

## ⚡ Résolution de Problèmes

### Port déjà utilisé
```bash
# Utiliser un autre port
streamlit run dashboard/app.py --server.port 8502
```

### Données non trouvées
```bash
# Vérifier la présence du fichier
ls -la data/processed/
```

### Modules manquants
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

## ✅ Checklist de Démo

- [ ] Environnement virtuel activé
- [ ] Dashboard lancé (http://localhost:8501)
- [ ] Données chargées correctement
- [ ] Navigation entre les 6 pages
- [ ] Filtres interactifs testés
- [ ] Export PDF/Excel testé

## 🎯 Points Clés pour la Démo

1. **Page Accueil:** Montrer la vue d'ensemble
2. **Analyse Médias:** Montrer le classement d'influence
3. **Contenus Sensibles:** Montrer la détection automatique avec filtres
4. **Export:** Générer et télécharger un rapport PDF

## 💡 Astuces

- Les graphiques Plotly sont interactifs (zoom, survol, filtres)
- Utilisez les filtres pour explorer les données
- Les rapports incluent un timestamp automatique
- Le dashboard utilise un cache pour meilleures performances

## 📞 Support

Questions? Consultez:
- **DASHBOARD_GUIDE.md** pour l'utilisation
- **dashboard/README.md** pour le développement

---

**MÉDIA-SCAN v1.0**
Développé pour le CSC - Burkina Faso
Hackathon AI 2025 - MTDPCE