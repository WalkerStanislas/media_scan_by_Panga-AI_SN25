"""
Composants UI réutilisables pour le dashboard
"""
import streamlit as st
from PIL import Image
import os
from pathlib import Path
from dashboard.media_config import get_media_logo_path, get_media_info, MEDIA_CONFIG


def display_media_logo(media_name, width=80, use_column_width=False):
    """
    Affiche le logo d'un média avec fallback sur initiales

    Args:
        media_name: Nom du média
        width: Largeur du logo en pixels
        use_column_width: Utiliser la largeur de la colonne

    Returns:
        True si le logo a été affiché, False sinon
    """
    logo_path = get_media_logo_path(media_name)

    if logo_path and os.path.exists(logo_path):
        try:
            image = Image.open(logo_path)
            st.image(image, width=width if not use_column_width else None,
                    use_column_width=use_column_width)
            return True
        except Exception as e:
            # En cas d'erreur, afficher les initiales
            st.markdown(f"""
                <div style="
                    width: {width}px;
                    height: {width}px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: {width//3}px;
                    margin: auto;
                ">
                    {media_name[:2].upper()}
                </div>
            """, unsafe_allow_html=True)
            return False
    else:
        # Afficher un placeholder avec les initiales
        initials = ''.join([word[0].upper() for word in media_name.split()[:2]])
        st.markdown(f"""
            <div style="
                width: {width}px;
                height: {width}px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                color: white;
                font-weight: bold;
                font-size: {width//3}px;
                margin: auto;
            ">
                {initials}
            </div>
        """, unsafe_allow_html=True)
        return False


def display_media_header():
    """
    Affiche un header professionnel avec les logos de tous les médias
    """
    st.markdown("""
        <style>
        .media-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .media-header-title {
            color: white;
            text-align: center;
            font-size: 1.5em;
            font-weight: 600;
            margin-bottom: 20px;
        }
        .media-logos-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .media-logo-wrapper {
            background: white;
            border-radius: 50%;
            padding: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            transition: transform 0.3s ease;
        }
        .media-logo-wrapper:hover {
            transform: scale(1.1);
        }
        </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="media-header">', unsafe_allow_html=True)
        st.markdown('<div class="media-header-title">🎯 Médias Analysés</div>', unsafe_allow_html=True)

        # Créer des colonnes pour afficher les logos
        medias_list = [name for name in MEDIA_CONFIG.keys() if MEDIA_CONFIG[name]['logo'] is not None]

        # Afficher les logos en ligne
        cols = st.columns(len(medias_list) if len(medias_list) <= 9 else 9)

        for idx, media_name in enumerate(medias_list[:9]):  # Limiter à 9 logos
            with cols[idx]:
                logo_path = get_media_logo_path(media_name)
                if logo_path and os.path.exists(logo_path):
                    try:
                        image = Image.open(logo_path)
                        st.image(image, use_column_width=True)
                        # Nom du média en petit sous le logo
                        st.markdown(f"<p style='text-align: center; font-size: 0.7em; color: white; margin-top: 5px;'>{media_name}</p>",
                                  unsafe_allow_html=True)
                    except:
                        # Fallback: initiales
                        initials = ''.join([word[0].upper() for word in media_name.split()[:2]])
                        st.markdown(f"""
                            <div style="
                                width: 60px;
                                height: 60px;
                                background: white;
                                border-radius: 50%;
                                display: flex;
                                align-items: center;
                                justify-content: center;
                                color: #667eea;
                                font-weight: bold;
                                font-size: 20px;
                                margin: auto;
                            ">
                                {initials}
                            </div>
                            <p style='text-align: center; font-size: 0.7em; color: white; margin-top: 5px;'>{media_name}</p>
                        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


def display_media_card(media_name, nb_articles, engagement_total, score_influence, rang):
    """
    Affiche une carte stylisée pour un média avec son logo

    Args:
        media_name: Nom du média
        nb_articles: Nombre d'articles
        engagement_total: Engagement total
        score_influence: Score d'influence
        rang: Rang du média
    """
    media_info = get_media_info(media_name)
    logo_path = get_media_logo_path(media_name)

    # Définir la couleur du rang (médaille)
    if rang == 1:
        rank_color = "#FFD700"  # Or
        rank_icon = "🥇"
    elif rang == 2:
        rank_color = "#C0C0C0"  # Argent
        rank_icon = "🥈"
    elif rang == 3:
        rank_color = "#CD7F32"  # Bronze
        rank_icon = "🥉"
    else:
        rank_color = "#95a5a6"
        rank_icon = f"#{rang}"

    # Créer un conteneur Streamlit avec bordure colorée
    with st.container():
        # Badge de rang aligné à droite
        col_empty, col_badge = st.columns([4, 1])
        with col_badge:
            st.markdown(f"""
                <span style="
                    background: {rank_color};
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                    font-size: 0.9em;
                    display: inline-block;
                ">{rank_icon}</span>
            """, unsafe_allow_html=True)

        # Contenu principal de la carte
        col_logo, col_info, col_stats = st.columns([1, 2, 2])

        with col_logo:
            if logo_path and os.path.exists(logo_path):
                try:
                    image = Image.open(logo_path)
                    st.image(image, width=80)
                except:
                    display_media_logo(media_name, width=80)
            else:
                display_media_logo(media_name, width=80)

        with col_info:
            st.markdown(f"### {media_name}")
            st.markdown(f"*{media_info['description']}*")
            st.markdown(f"**Type:** {media_info['type'].capitalize()}")
            if media_info['url']:
                st.markdown(f"[🌐 Visiter]({media_info['url']})")

        with col_stats:
            st.metric("📰 Articles", f"{nb_articles:,}")
            st.metric("💬 Engagement", f"{engagement_total:,}")
            st.metric("⭐ Score Influence", f"{score_influence:.2f}")

        # Ligne de séparation avec couleur du rang
        st.markdown(f"""
            <hr style="
                border: none;
                height: 2px;
                background: linear-gradient(to right, {rank_color}, transparent);
                margin: 20px 0;
            ">
        """, unsafe_allow_html=True)


def display_compact_media_badge(media_name, show_type=True):
    """
    Affiche un badge compact avec logo et nom du média

    Args:
        media_name: Nom du média
        show_type: Afficher le type de média (web/facebook)
    """
    media_info = get_media_info(media_name)
    logo_path = get_media_logo_path(media_name)

    # Couleur selon le type
    type_colors = {
        'web': '#3498db',
        'facebook': '#4267B2',
        'activiste': '#e74c3c'
    }

    color = type_colors.get(media_info['type'], '#95a5a6')

    col1, col2 = st.columns([1, 4])

    with col1:
        if logo_path and os.path.exists(logo_path):
            try:
                image = Image.open(logo_path)
                st.image(image, width=40)
            except:
                st.markdown(f"**{media_name[:2]}**")
        else:
            st.markdown(f"**{media_name[:2]}**")

    with col2:
        st.markdown(f"**{media_name}**")
        if show_type:
            st.markdown(f'<span style="background-color: {color}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 0.8em;">{media_info["type"]}</span>',
                       unsafe_allow_html=True)


def display_toxicity_badge(score):
    """
    Affiche un badge de toxicité avec couleur appropriée

    Args:
        score: Score de toxicité (0.0 - 1.0)
    """
    if score >= 0.7:
        color = "#e74c3c"
        icon = "🔴"
        level = "ÉLEVÉ"
    elif score >= 0.3:
        color = "#f39c12"
        icon = "🟡"
        level = "MOYEN"
    else:
        color = "#2ecc71"
        icon = "🟢"
        level = "FAIBLE"

    st.markdown(f"""
        <div style="
            background-color: {color};
            color: white;
            padding: 10px 20px;
            border-radius: 10px;
            text-align: center;
            font-weight: bold;
        ">
            {icon} {level}: {score:.2f}
        </div>
    """, unsafe_allow_html=True)


def display_stat_card(title, value, icon="📊", delta=None, delta_color="normal"):
    """
    Affiche une carte de statistique stylisée

    Args:
        title: Titre de la statistique
        value: Valeur à afficher
        icon: Icône à afficher
        delta: Variation (optionnel)
        delta_color: Couleur du delta (normal, inverse, off)
    """
    delta_html = ""
    if delta is not None:
        delta_sign = "+" if delta > 0 else ""
        delta_color_val = "#2ecc71" if delta > 0 else "#e74c3c"
        delta_html = f'<div style="color: {delta_color_val}; font-size: 0.9em; margin-top: 5px;">{delta_sign}{delta}%</div>'

    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 0.9em; opacity: 0.9; margin-bottom: 5px;">{title}</div>
            <div style="font-size: 2em; font-weight: bold;">{value}</div>
            {delta_html}
        </div>
    """, unsafe_allow_html=True)


def display_comment_alert_badge(alert_type, nb_comments_sensibles=0, nb_highly_toxic=0, max_toxicity=0.0):
    """
    Affiche un badge d'alerte pour les commentaires suspects

    Args:
        alert_type: Type d'alerte ('critical', 'mass', 'critical_mass')
        nb_comments_sensibles: Nombre de commentaires marqués sensibles
        nb_highly_toxic: Nombre de commentaires très toxiques (>0.8)
        max_toxicity: Score de toxicité maximum
    """
    if alert_type == 'critical_mass':
        color = "#8B0000"  # Rouge foncé
        icon = "🚨"
        title = "ALERTE CRITIQUE"
        description = f"{nb_comments_sensibles} commentaire(s) dangereux + volume élevé"
    elif alert_type == 'critical':
        color = "#e74c3c"  # Rouge
        icon = "⚠️"
        title = "ALERTE"
        description = f"{nb_comments_sensibles + nb_highly_toxic} commentaire(s) très toxique(s)"
    elif alert_type == 'mass':
        color = "#f39c12"  # Orange
        icon = "📢"
        title = "VIGILANCE"
        description = "Volume élevé de commentaires suspects"
    else:
        return

    st.markdown(f"""
        <div style="
            background-color: {color};
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 5px solid rgba(255,255,255,0.3);
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            animation: pulse 2s infinite;
        ">
            <div style="display: flex; align-items: center; gap: 10px;">
                <span style="font-size: 1.5em;">{icon}</span>
                <div style="flex: 1;">
                    <div style="font-weight: bold; font-size: 1.1em;">{title}</div>
                    <div style="font-size: 0.9em; opacity: 0.95;">{description}</div>
                    <div style="font-size: 0.85em; margin-top: 5px; opacity: 0.9;">
                        Score max: {max_toxicity:.2f}
                    </div>
                </div>
            </div>
        </div>
        <style>
            @keyframes pulse {{
                0%, 100% {{ opacity: 1; }}
                50% {{ opacity: 0.9; }}
            }}
        </style>
    """, unsafe_allow_html=True)


def display_comment_alert_icon(alert_type):
    """
    Affiche une petite icône d'alerte à côté d'un article

    Args:
        alert_type: Type d'alerte ('critical', 'mass', 'critical_mass')
    """
    if alert_type == 'critical_mass':
        icon = "🚨"
        tooltip = "Commentaires dangereux détectés + volume élevé"
    elif alert_type == 'critical':
        icon = "⚠️"
        tooltip = "Commentaires très toxiques détectés"
    elif alert_type == 'mass':
        icon = "📢"
        tooltip = "Volume élevé de commentaires suspects"
    else:
        return

    st.markdown(f"""
        <span style="
            font-size: 1.2em;
            cursor: help;
        " title="{tooltip}">{icon}</span>
    """, unsafe_allow_html=True)