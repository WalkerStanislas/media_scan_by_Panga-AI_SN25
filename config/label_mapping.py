"""
Mapping et normalisation des labels pour l'entraînement du modèle de classification
Uniformise les différentes variantes de catégories/rubriques en labels standardisés
"""

# Labels standardisés pour la classification
STANDARD_LABELS = [
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

# Mapping des catégories brutes vers les labels standardisés
# Clés en minuscules pour faciliter la correspondance
CATEGORY_TO_LABEL = {
    # Politique
    "politique": "Politique",
    "politiques": "Politique",
    "gouvernement": "Politique",
    "parlement": "Politique",
    "assemblée": "Politique",
    "élection": "Politique",
    "elections": "Politique",

    # Économie
    "economie": "Économie",
    "économie": "Économie",
    "finance": "Économie",
    "finances": "Économie",
    "budget": "Économie",
    "commerce": "Économie",
    "entreprise": "Économie",
    "entreprises": "Économie",
    "économique": "Économie",

    # Sécurité
    "securite": "Sécurité",
    "sécurité": "Sécurité",
    "defense": "Sécurité",
    "défense": "Sécurité",
    "armée": "Sécurité",
    "militaire": "Sécurité",
    "police": "Sécurité",
    "terrorisme": "Sécurité",
    "justice": "Sécurité",
    "nouvelle-du-front": "Sécurité",

    # Santé
    "sante": "Santé",
    "santé": "Santé",
    "medical": "Santé",
    "médical": "Santé",
    "hopital": "Santé",
    "hôpital": "Santé",
    "covid": "Santé",
    "pandemie": "Santé",
    "pandémie": "Santé",

    # Culture
    "culture": "Culture",
    "cultures": "Culture",
    "art": "Culture",
    "arts": "Culture",
    "festival": "Culture",
    "festivals": "Culture",
    "musique": "Culture",
    "cinema": "Culture",
    "cinéma": "Culture",
    "theatre": "Culture",
    "théâtre": "Culture",
    "patrimoine": "Culture",

    # Sport
    "sport": "Sport",
    "sports": "Sport",
    "football": "Sport",
    "basketball": "Sport",
    "athletisme": "Sport",
    "athlétisme": "Sport",
    "competition": "Sport",
    "compétition": "Sport",

    # International
    "international": "International",
    "monde": "International",
    "afrique": "International",
    "europe": "International",
    "amerique": "International",
    "amérique": "International",
    "asie": "International",
    "diplomatie": "International",
    "cooperation": "International",
    "coopération": "International",

    # Société
    "societe": "Société",
    "société": "Société",
    "social": "Société",
    "education": "Société",
    "éducation": "Société",
    "jeunesse": "Société",
    "femme": "Société",
    "femmes": "Société",
    "enfant": "Société",
    "enfants": "Société",
    "famille": "Société",
    "environnement": "Société",
    "religion": "Société",

    # Divers (AIB spécifique)
    "depeches": "Autre",
    "dépêches": "Autre",
    "evenements": "Autre",
    "événements": "Autre",
    "medias": "Autre",
    "médias": "Autre",
}


def normalize_label(category_raw: str) -> str:
    """
    Normalise une catégorie/rubrique brute en label standardisé

    Args:
        category_raw: Catégorie brute extraite du site

    Returns:
        Label standardisé (ex: "Politique", "Sport", etc.)
    """
    if not category_raw:
        return "Autre"

    # Nettoyer et convertir en minuscule
    category_clean = category_raw.strip().lower()

    # Chercher dans le mapping
    label = CATEGORY_TO_LABEL.get(category_clean, None)

    if label:
        return label

    # Si pas de correspondance exacte, chercher par mots-clés
    for key, value in CATEGORY_TO_LABEL.items():
        if key in category_clean or category_clean in key:
            return value

    # Par défaut
    return "Autre"


def get_label_distribution(articles: list) -> dict:
    """
    Calcule la distribution des labels dans un ensemble d'articles

    Args:
        articles: Liste d'articles avec leurs labels

    Returns:
        Dict avec le comptage par label
    """
    distribution = {label: 0 for label in STANDARD_LABELS}

    for article in articles:
        label = article.get('label', 'Autre')
        if label in distribution:
            distribution[label] += 1
        else:
            distribution['Autre'] += 1

    return distribution


def validate_label(label: str) -> bool:
    """
    Vérifie si un label est valide

    Args:
        label: Label à vérifier

    Returns:
        True si le label est dans STANDARD_LABELS
    """
    return label in STANDARD_LABELS
