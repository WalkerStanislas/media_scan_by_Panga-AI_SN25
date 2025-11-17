"""
MÉDIA-SCAN - Dashboard Interactif
Application Streamlit pour l'analyse des médias burkinabè
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour les imports
sys.path.append(str(Path(__file__).parent.parent))

from dashboard.data_loader import DataLoader
from dashboard.report_generator import ReportGenerator

# Configuration de la page
st.set_page_config(
    page_title="MÉDIA-SCAN - Dashboard CSC",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #1f77b4;
    }
    .reportview-container .markdown-text-container {
        font-family: 'Arial', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialisation de la session
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.data_loader = None

# Fonction pour charger les données
@st.cache_data
def load_data():
    """Charge les données depuis le fichier JSON"""
    loader = DataLoader()
    try:
        loader.load_data("sample_data.json")
        return loader
    except FileNotFoundError:
        st.error("Fichier de données introuvable. Veuillez vérifier que le fichier existe dans data/processed/")
        return None

# Sidebar - Navigation
st.sidebar.title("📰 MÉDIA-SCAN")
st.sidebar.markdown("---")
st.sidebar.markdown("**Système d'Observation et d'Analyse des Médias**")
st.sidebar.markdown("*Conseil Supérieur de la Communication*")
st.sidebar.markdown("---")

# Menu de navigation
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "📊 Analyse des Médias", "📑 Analyse Thématique",
     "⚠️ Contenus Sensibles", "📈 Engagement", "📥 Exporter les Rapports"]
)

# Bouton de rechargement des données
st.sidebar.markdown("---")
if st.sidebar.button("🔄 Recharger les données"):
    st.cache_data.clear()
    st.session_state.data_loaded = False
    st.rerun()

# Chargement des données
if not st.session_state.data_loaded:
    with st.spinner("Chargement des données..."):
        data_loader = load_data()
        if data_loader:
            st.session_state.data_loader = data_loader
            st.session_state.data_loaded = True
        else:
            st.stop()

data_loader = st.session_state.data_loader

# Affichage de la date de dernière mise à jour
if data_loader and data_loader.articles_df is not None and not data_loader.articles_df.empty:
    last_update = data_loader.articles_df['date'].max()
    st.sidebar.markdown("---")
    st.sidebar.info(f"📅 Dernière mise à jour: {last_update.strftime('%d/%m/%Y')}")

# ============================================================================
# PAGE 1: ACCUEIL - Vue d'ensemble
# ============================================================================
if page == "🏠 Accueil":
    st.title("🏠 Tableau de Bord - Vue d'Ensemble")
    st.markdown("### Statistiques Globales du Paysage Médiatique Burkinabè")

    # Statistiques globales
    stats = data_loader.get_global_stats()

    # Affichage des métriques principales
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📰 Total Articles",
            value=f"{stats.get('total_articles', 0):,}",
            delta=None
        )

    with col2:
        st.metric(
            label="📺 Médias Analysés",
            value=stats.get('total_medias', 0),
            delta=None
        )

    with col3:
        st.metric(
            label="💬 Engagement Total",
            value=f"{stats.get('total_engagement', 0):,}",
            delta=None
        )

    with col4:
        st.metric(
            label="⚠️ Articles Sensibles",
            value=stats.get('articles_sensibles', 0),
            delta=f"{stats.get('taux_sensible', 0):.1f}%"
        )

    st.markdown("---")

    # Graphiques principaux
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Distribution par Catégorie")
        category_dist = data_loader.get_category_distribution()
        if category_dist:
            fig = px.pie(
                names=list(category_dist.keys()),
                values=list(category_dist.values()),
                title="Répartition des Articles par Thématique",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### 📺 Articles par Média")
        media_stats = data_loader.get_articles_by_media()
        if not media_stats.empty:
            fig = px.bar(
                media_stats,
                x='Média',
                y='Nombre d\'articles',
                title="Volume de Publication par Média",
                color='Engagement total',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

    # Timeline
    st.markdown("---")
    st.markdown("#### 📅 Évolution Temporelle des Publications")

    timeline_data = data_loader.get_timeline_data(days=30)
    if not timeline_data.empty:
        fig = px.line(
            timeline_data,
            x='Date',
            y='Nombre d\'articles',
            title="Nombre d'articles publiés par jour (30 derniers jours)",
            markers=True
        )
        fig.update_traces(line_color='#1f77b4', line_width=2)
        st.plotly_chart(fig, use_container_width=True)

    # Top articles
    st.markdown("---")
    st.markdown("#### 🏆 Top 10 Articles par Engagement")

    top_articles = data_loader.get_top_articles(n=10)
    if not top_articles.empty:
        for idx, article in top_articles.iterrows():
            with st.expander(f"#{idx+1} - {article['titre'][:80]}..."):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**Média:** {article['media']}")
                    st.write(f"**Catégorie:** {article['categorie']}")
                with col2:
                    st.write(f"**Date:** {article['date'].strftime('%d/%m/%Y')}")
                with col3:
                    st.write(f"**Engagement:** {article['score']:,}")
                st.write(f"**URL:** {article['url']}")

# ============================================================================
# PAGE 2: ANALYSE DES MÉDIAS
# ============================================================================
elif page == "📊 Analyse des Médias":
    st.title("📊 Analyse des Médias")
    st.markdown("### Classement et Performance des Médias Burkinabè")

    # Classement des médias
    media_ranking = data_loader.get_media_ranking()

    if not media_ranking.empty:
        st.markdown("#### 🏆 Classement Global des Médias")

        # Affichage du tableau
        st.dataframe(
            media_ranking.style.background_gradient(
                subset=['score_influence'],
                cmap='RdYlGn'
            ),
            use_container_width=True
        )

        st.markdown("---")

        # Visualisations
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📈 Score d'Influence")
            fig = px.bar(
                media_ranking,
                x='nom',
                y='score_influence',
                title="Score d'Influence par Média",
                color='score_influence',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 📰 Volume de Publications")
            fig = px.bar(
                media_ranking,
                x='nom',
                y='nb_articles',
                title="Nombre d'Articles par Média",
                color='nb_articles',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Engagement total
        st.markdown("#### 💬 Engagement Total par Média")
        fig = px.scatter(
            media_ranking,
            x='nb_articles',
            y='engagement_total',
            size='score_influence',
            color='nom',
            title="Relation entre Volume et Engagement",
            hover_data=['nom', 'score_influence'],
            size_max=60
        )
        st.plotly_chart(fig, use_container_width=True)

        # Détails par média
        st.markdown("---")
        st.markdown("#### 🔍 Détails par Média")

        selected_media = st.selectbox(
            "Sélectionnez un média pour voir les détails",
            media_ranking['nom'].tolist()
        )

        if selected_media:
            media_articles = data_loader.articles_df[
                data_loader.articles_df['media'] == selected_media
            ].copy()

            if not media_articles.empty:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Articles publiés", len(media_articles))

                with col2:
                    total_eng = media_articles['engagement'].apply(
                        lambda x: x.get('likes', 0) + x.get('partages', 0) + x.get('commentaires', 0)
                    ).sum()
                    st.metric("Engagement total", f"{total_eng:,}")

                with col3:
                    sensitive_count = len(media_articles[media_articles['sensible'] == True])
                    st.metric("Articles sensibles", sensitive_count)

                # Distribution des catégories pour ce média
                st.markdown("##### Distribution Thématique")
                cat_dist = media_articles['categorie'].value_counts()
                fig = px.bar(
                    x=cat_dist.index,
                    y=cat_dist.values,
                    labels={'x': 'Catégorie', 'y': 'Nombre d\'articles'},
                    title=f"Répartition thématique - {selected_media}"
                )
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE 3: ANALYSE THÉMATIQUE
# ============================================================================
elif page == "📑 Analyse Thématique":
    st.title("📑 Analyse Thématique")
    st.markdown("### Distribution et Engagement par Thématique")

    # Statistiques par catégorie
    category_stats = data_loader.get_articles_by_category()
    engagement_by_cat = data_loader.get_engagement_by_category()

    if not category_stats.empty:
        # Vue d'ensemble
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📊 Nombre d'Articles par Catégorie")
            fig = px.bar(
                category_stats,
                x='Catégorie',
                y='Nombre d\'articles',
                color='Catégorie',
                title="Volume par Thématique"
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 💬 Engagement par Catégorie")
            fig = px.bar(
                category_stats,
                x='Catégorie',
                y='Engagement total',
                color='Engagement total',
                color_continuous_scale='Viridis',
                title="Engagement Total par Thématique"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Tableau détaillé
        st.markdown("#### 📋 Tableau Détaillé")
        st.dataframe(category_stats, use_container_width=True)

        st.markdown("---")

        # Engagement détaillé
        if not engagement_by_cat.empty:
            st.markdown("#### 📊 Détail de l'Engagement par Type")

            fig = go.Figure()
            fig.add_trace(go.Bar(name='Likes', x=engagement_by_cat['categorie'], y=engagement_by_cat['likes']))
            fig.add_trace(go.Bar(name='Partages', x=engagement_by_cat['categorie'], y=engagement_by_cat['partages']))
            fig.add_trace(go.Bar(name='Commentaires', x=engagement_by_cat['categorie'], y=engagement_by_cat['commentaires']))

            fig.update_layout(
                barmode='group',
                title="Répartition de l'Engagement par Type et Catégorie",
                xaxis_title="Catégorie",
                yaxis_title="Nombre",
                hovermode='x unified'
            )
            st.plotly_chart(fig, use_container_width=True)

        # Analyse par catégorie sélectionnée
        st.markdown("---")
        st.markdown("#### 🔍 Analyse Détaillée par Catégorie")

        selected_category = st.selectbox(
            "Sélectionnez une catégorie",
            category_stats['Catégorie'].tolist()
        )

        if selected_category:
            cat_articles = data_loader.articles_df[
                data_loader.articles_df['categorie'] == selected_category
            ].copy()

            if not cat_articles.empty:
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Nombre d'articles", len(cat_articles))

                with col2:
                    avg_engagement = cat_articles['engagement'].apply(
                        lambda x: x.get('likes', 0) + x.get('partages', 0) + x.get('commentaires', 0)
                    ).mean()
                    st.metric("Engagement moyen", f"{avg_engagement:.0f}")

                with col3:
                    media_count = cat_articles['media'].nunique()
                    st.metric("Médias contributeurs", media_count)

                # Répartition par média dans cette catégorie
                st.markdown("##### Contribution par Média")
                media_dist = cat_articles['media'].value_counts()
                fig = px.pie(
                    names=media_dist.index,
                    values=media_dist.values,
                    title=f"Médias contributeurs - {selected_category}"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Articles récents
                st.markdown("##### Articles Récents")
                recent = cat_articles.nlargest(5, 'date')[['titre', 'media', 'date', 'url']]
                for idx, article in recent.iterrows():
                    st.write(f"**{article['titre']}**")
                    st.write(f"_{article['media']} - {article['date'].strftime('%d/%m/%Y')}_")
                    st.write(f"[Lien]({article['url']})")
                    st.write("---")

# ============================================================================
# PAGE 4: CONTENUS SENSIBLES
# ============================================================================
elif page == "⚠️ Contenus Sensibles":
    st.title("⚠️ Détection de Contenus Sensibles")
    st.markdown("### Surveillance et Analyse des Contenus à Risque")

    # Seuil de toxicité
    toxicity_threshold = st.slider(
        "Seuil de toxicité minimum",
        min_value=0.0,
        max_value=1.0,
        value=0.3,
        step=0.05
    )

    sensitive_articles = data_loader.get_sensitive_articles(min_toxicity=toxicity_threshold)

    # Statistiques
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Contenus Sensibles Détectés",
            len(sensitive_articles)
        )

    with col2:
        if not sensitive_articles.empty:
            avg_toxicity = sensitive_articles['toxicite_score'].mean()
            st.metric(
                "Score de Toxicité Moyen",
                f"{avg_toxicity:.2f}"
            )
        else:
            st.metric("Score de Toxicité Moyen", "N/A")

    with col3:
        if not sensitive_articles.empty:
            max_toxicity = sensitive_articles['toxicite_score'].max()
            st.metric(
                "Score Maximum",
                f"{max_toxicity:.2f}"
            )
        else:
            st.metric("Score Maximum", "N/A")

    st.markdown("---")

    if not sensitive_articles.empty:
        # Distribution par média
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📺 Répartition par Média")
            media_dist = sensitive_articles['media'].value_counts()
            fig = px.bar(
                x=media_dist.index,
                y=media_dist.values,
                labels={'x': 'Média', 'y': 'Nombre de contenus sensibles'},
                title="Contenus Sensibles par Média"
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("#### 📑 Répartition par Catégorie")
            cat_dist = sensitive_articles['categorie'].value_counts()
            fig = px.pie(
                names=cat_dist.index,
                values=cat_dist.values,
                title="Contenus Sensibles par Thématique"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Distribution des scores de toxicité
        st.markdown("#### 📊 Distribution des Scores de Toxicité")
        fig = px.histogram(
            sensitive_articles,
            x='toxicite_score',
            nbins=20,
            title="Distribution des Scores de Toxicité",
            labels={'toxicite_score': 'Score de Toxicité', 'count': 'Nombre d\'articles'}
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Liste des contenus sensibles
        st.markdown("#### 📋 Liste des Contenus Sensibles")

        # Filtres
        col1, col2 = st.columns(2)

        with col1:
            filter_media = st.multiselect(
                "Filtrer par média",
                options=sensitive_articles['media'].unique().tolist(),
                default=[]
            )

        with col2:
            filter_category = st.multiselect(
                "Filtrer par catégorie",
                options=sensitive_articles['categorie'].unique().tolist(),
                default=[]
            )

        # Appliquer les filtres
        filtered_sensitive = sensitive_articles.copy()
        if filter_media:
            filtered_sensitive = filtered_sensitive[filtered_sensitive['media'].isin(filter_media)]
        if filter_category:
            filtered_sensitive = filtered_sensitive[filtered_sensitive['categorie'].isin(filter_category)]

        # Affichage
        st.write(f"**{len(filtered_sensitive)} contenus affichés**")

        for idx, article in filtered_sensitive.iterrows():
            with st.expander(f"[Score: {article['toxicite_score']:.2f}] {article['titre']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Média:** {article['media']}")
                    st.write(f"**Catégorie:** {article['categorie']}")
                    st.write(f"**Date:** {article['date'].strftime('%d/%m/%Y')}")
                    st.write(f"**URL:** {article['url']}")
                with col2:
                    # Indicateur visuel du score
                    if article['toxicite_score'] >= 0.7:
                        st.error(f"🔴 Score: {article['toxicite_score']:.2f}")
                    elif article['toxicite_score'] >= 0.5:
                        st.warning(f"🟡 Score: {article['toxicite_score']:.2f}")
                    else:
                        st.info(f"🔵 Score: {article['toxicite_score']:.2f}")
    else:
        st.info("Aucun contenu sensible détecté avec le seuil actuel.")

# ============================================================================
# PAGE 5: ENGAGEMENT
# ============================================================================
elif page == "📈 Engagement":
    st.title("📈 Analyse de l'Engagement")
    st.markdown("### Métriques d'Interaction et d'Audience")

    stats = data_loader.get_global_stats()

    # Métriques globales
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("👍 Total Likes", f"{stats.get('total_likes', 0):,}")

    with col2:
        st.metric("🔄 Total Partages", f"{stats.get('total_partages', 0):,}")

    with col3:
        st.metric("💬 Total Commentaires", f"{stats.get('total_commentaires', 0):,}")

    st.markdown("---")

    # Engagement par catégorie
    engagement_by_cat = data_loader.get_engagement_by_category()

    if not engagement_by_cat.empty:
        st.markdown("#### 📊 Engagement par Catégorie")

        # Graphique en barres empilées
        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Likes',
            x=engagement_by_cat['categorie'],
            y=engagement_by_cat['likes'],
            marker_color='rgb(55, 83, 109)'
        ))
        fig.add_trace(go.Bar(
            name='Partages',
            x=engagement_by_cat['categorie'],
            y=engagement_by_cat['partages'],
            marker_color='rgb(26, 118, 255)'
        ))
        fig.add_trace(go.Bar(
            name='Commentaires',
            x=engagement_by_cat['categorie'],
            y=engagement_by_cat['commentaires'],
            marker_color='rgb(50, 171, 96)'
        ))

        fig.update_layout(
            barmode='stack',
            title="Engagement Total par Catégorie (Empilé)",
            xaxis_title="Catégorie",
            yaxis_title="Nombre d'interactions",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Taux d'engagement moyen
        st.markdown("#### 📊 Taux d'Engagement Moyen par Catégorie")

        category_stats = data_loader.get_articles_by_category()
        if not category_stats.empty:
            engagement_rate = engagement_by_cat.merge(
                category_stats[['Catégorie', 'Nombre d\'articles']],
                left_on='categorie',
                right_on='Catégorie'
            )
            engagement_rate['taux_engagement'] = (
                engagement_rate['total_engagement'] / engagement_rate['Nombre d\'articles']
            )

            fig = px.bar(
                engagement_rate,
                x='categorie',
                y='taux_engagement',
                title="Engagement Moyen par Article et par Catégorie",
                labels={'categorie': 'Catégorie', 'taux_engagement': 'Engagement moyen'},
                color='taux_engagement',
                color_continuous_scale='Viridis'
            )
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Engagement par média
    media_stats = data_loader.get_articles_by_media()

    if not media_stats.empty:
        st.markdown("#### 📺 Engagement par Média")

        fig = px.bar(
            media_stats,
            x='Média',
            y='Engagement total',
            title="Engagement Total par Média",
            color='Engagement total',
            color_continuous_scale='Blues'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

        # Engagement moyen par article
        media_stats['engagement_moyen'] = (
            media_stats['Engagement total'] / media_stats['Nombre d\'articles']
        )

        st.markdown("#### 📊 Engagement Moyen par Article")
        fig = px.bar(
            media_stats,
            x='Média',
            y='engagement_moyen',
            title="Engagement Moyen par Article et par Média",
            color='engagement_moyen',
            color_continuous_scale='Greens'
        )
        fig.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Top articles par type d'engagement
    st.markdown("#### 🏆 Top Articles par Type d'Engagement")

    engagement_type = st.radio(
        "Sélectionnez le type d'engagement",
        ["engagement", "likes", "partages", "commentaires"],
        horizontal=True
    )

    top_by_type = data_loader.get_top_articles(n=10, metric=engagement_type)

    if not top_by_type.empty:
        for idx, article in top_by_type.iterrows():
            with st.expander(f"#{idx+1} - {article['titre'][:80]}..."):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Média:** {article['media']}")
                    st.write(f"**Catégorie:** {article['categorie']}")
                    st.write(f"**Date:** {article['date'].strftime('%d/%m/%Y')}")
                    st.write(f"**URL:** {article['url']}")
                with col2:
                    metric_label = {
                        'engagement': 'Engagement Total',
                        'likes': 'Likes',
                        'partages': 'Partages',
                        'commentaires': 'Commentaires'
                    }
                    st.metric(metric_label[engagement_type], f"{article['score']:,}")

# ============================================================================
# PAGE 6: EXPORT DE RAPPORTS
# ============================================================================
elif page == "📥 Exporter les Rapports":
    st.title("📥 Exporter les Rapports")
    st.markdown("### Générer et Télécharger les Rapports d'Analyse")

    st.info("💡 Vous pouvez générer et télécharger des rapports complets au format Excel ou PDF.")

    # Initialiser le générateur de rapports
    report_gen = ReportGenerator(data_loader)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📊 Rapport Excel")
        st.write("Rapport complet avec tous les onglets de données détaillées:")
        st.write("- Statistiques globales")
        st.write("- Classement des médias")
        st.write("- Articles par catégorie")
        st.write("- Engagement détaillé")
        st.write("- Contenus sensibles")
        st.write("- Liste complète des articles")

        if st.button("📥 Générer le Rapport Excel", key="excel_btn"):
            with st.spinner("Génération du rapport Excel..."):
                try:
                    excel_data = report_gen.generate_excel_report()

                    st.download_button(
                        label="⬇️ Télécharger le Rapport Excel",
                        data=excel_data,
                        file_name=f"media_scan_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                    st.success("✅ Rapport Excel généré avec succès!")
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")

    with col2:
        st.markdown("#### 📄 Rapport PDF")
        st.write("Rapport synthétique avec les principales statistiques:")
        st.write("- Vue d'ensemble")
        st.write("- Classement des médias")
        st.write("- Distribution thématique")
        st.write("- Contenus sensibles")
        st.write("- Top articles")

        if st.button("📥 Générer le Rapport PDF", key="pdf_btn"):
            with st.spinner("Génération du rapport PDF..."):
                try:
                    pdf_data = report_gen.generate_pdf_report()

                    st.download_button(
                        label="⬇️ Télécharger le Rapport PDF",
                        data=pdf_data,
                        file_name=f"media_scan_rapport_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ Rapport PDF généré avec succès!")
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération: {str(e)}")

    st.markdown("---")

    # Export JSON
    st.markdown("#### 💾 Export JSON")
    st.write("Export des données brutes au format JSON pour intégration avec d'autres systèmes.")

    if st.button("📥 Générer l'Export JSON", key="json_btn"):
        with st.spinner("Génération de l'export JSON..."):
            try:
                json_data = report_gen.generate_json_report()

                st.download_button(
                    label="⬇️ Télécharger l'Export JSON",
                    data=json_data,
                    file_name=f"media_scan_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                st.success("✅ Export JSON généré avec succès!")
            except Exception as e:
                st.error(f"❌ Erreur lors de la génération: {str(e)}")

    st.markdown("---")

    # Aperçu des statistiques
    st.markdown("#### 📊 Aperçu des Statistiques à Exporter")

    stats = data_loader.get_global_stats()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Articles", stats.get('total_articles', 0))
        st.metric("Médias", stats.get('total_medias', 0))

    with col2:
        st.metric("Engagement Total", f"{stats.get('total_engagement', 0):,}")
        st.metric("Likes", f"{stats.get('total_likes', 0):,}")

    with col3:
        st.metric("Partages", f"{stats.get('total_partages', 0):,}")
        st.metric("Commentaires", f"{stats.get('total_commentaires', 0):,}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### À propos")
st.sidebar.info(
    """
    **MÉDIA-SCAN v1.0**

    Développé pour le Conseil Supérieur
    de la Communication (CSC) du Burkina Faso.

    **Hackathon AI 2025 - MTDPCE**

    Axe: Gouvernance & Transparence Médiatique
    """
)