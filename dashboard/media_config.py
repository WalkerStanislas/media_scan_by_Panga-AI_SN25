"""
Configuration des médias burkinabè
Informations sur les médias, logos, et métadonnées
"""

# Mapping des noms de médias vers leurs configurations
MEDIA_CONFIG = {
    "Lefaso.net": {
        "nom_complet": "Lefaso.net",
        "logo": "lefaso.jpg",
        "type": "web",
        "description": "Premier site d'information burkinabè",
        "url": "https://lefaso.net"
    },
    "FasoPresse": {
        "nom_complet": "FasoPresse",
        "logo": "fasopresse.jpg",
        "type": "web",
        "description": "Agence de presse burkinabè",
        "url": "https://fasopresse.bf"
    },
    "Sidwaya": {
        "nom_complet": "Sidwaya",
        "logo": "sidwaya.png",
        "type": "web",
        "description": "Quotidien d'information burkinabè",
        "url": "https://sidwaya.info"
    },
    "AIB": {
        "nom_complet": "Agence d'Information du Burkina",
        "logo": "aib.jpeg",
        "type": "web",
        "description": "Agence d'information du Burkina Faso",
        "url": "https://aib.bf"
    },
    "L'Observateur Paalga": {
        "nom_complet": "L'Observateur Paalga",
        "logo": "lobservateur.png",
        "type": "web",
        "description": "Journal d'information burkinabè",
        "url": "https://lobservateur.bf"
    },
    "RTB": {
        "nom_complet": "Radiodiffusion Télévision du Burkina",
        "logo": "rtb.jpg",
        "type": "facebook",
        "description": "Télévision nationale du Burkina Faso",
        "url": "https://facebook.com/rtbofficiel"
    },
    "BF1": {
        "nom_complet": "BF1",
        "logo": "bf1.jpg",
        "type": "facebook",
        "description": "Chaîne de télévision burkinabè",
        "url": "https://facebook.com/bf1officiel"
    },
    "Omega Radio": {
        "nom_complet": "Oméga Radio",
        "logo": "omega.jpeg",
        "type": "facebook",
        "description": "Station de radio burkinabè",
        "url": "https://facebook.com/omegaradio"
    },
    # Média supplémentaire à configurer
    "Autre Média": {
        "nom_complet": "Autre Média",
        "logo": "autre_media.png",
        "type": "web",
        "description": "Média burkinabè",
        "url": ""
    },
    # Activiste (pas de logo nécessaire)
    "Naim Touré": {
        "nom_complet": "Naim Touré",
        "logo": None,  # Pas de logo pour l'activiste
        "type": "activiste",
        "description": "Activiste et commentateur",
        "url": ""
    }
}

# Catégories de couleurs pour les graphiques
CATEGORY_COLORS = {
    "Politique": "#FF6B6B",
    "Économie": "#4ECDC4",
    "Sécurité": "#FFE66D",
    "Santé": "#95E1D3",
    "Culture": "#F38181",
    "Sport": "#AA96DA",
    "Autres": "#FCBAD3"
}

# Configuration des seuils de toxicité
TOXICITY_LEVELS = {
    "faible": {"min": 0.0, "max": 0.3, "color": "#95E1D3", "icon": "🔵"},
    "moyen": {"min": 0.3, "max": 0.7, "color": "#FFE66D", "icon": "🟡"},
    "elevé": {"min": 0.7, "max": 1.0, "color": "#FF6B6B", "icon": "🔴"}
}

def get_media_logo_path(media_name: str) -> str:
    """
    Retourne le chemin vers le logo d'un média

    Args:
        media_name: Nom du média

    Returns:
        Chemin vers le fichier logo ou None si pas de logo
    """
    config = MEDIA_CONFIG.get(media_name, {})
    logo = config.get("logo")

    if logo:
        return f"assets/logos/{logo}"
    return None

def get_media_info(media_name: str) -> dict:
    """
    Retourne les informations complètes d'un média

    Args:
        media_name: Nom du média

    Returns:
        Dictionnaire avec les informations du média
    """
    return MEDIA_CONFIG.get(media_name, {
        "nom_complet": media_name,
        "logo": None,
        "type": "inconnu",
        "description": "",
        "url": ""
    })

def get_media_type_label(media_type: str) -> str:
    """
    Retourne le label d'affichage pour un type de média

    Args:
        media_type: Type de média (web, facebook, activiste)

    Returns:
        Label d'affichage
    """
    labels = {
        "web": "Site Web",
        "facebook": "Facebook",
        "activiste": "Activiste",
        "inconnu": "Autre"
    }
    return labels.get(media_type, "Autre")

def get_toxicity_level(score: float) -> dict:
    """
    Détermine le niveau de toxicité basé sur le score

    Args:
        score: Score de toxicité (0.0 à 1.0)

    Returns:
        Dictionnaire avec les informations du niveau
    """
    for level, config in TOXICITY_LEVELS.items():
        if config["min"] <= score < config["max"]:
            return {"level": level, **config}

    # Par défaut, élevé si >= 0.7
    return {"level": "elevé", **TOXICITY_LEVELS["elevé"]}

def normalize_media_name(media_name: str) -> str:
    """
    Normalise le nom d'un média pour correspondre à la configuration

    Args:
        media_name: Nom brut du média

    Returns:
        Nom normalisé
    """
    # Mapping de variations de noms vers les noms standards
    name_mapping = {
        "lefaso": "Lefaso.net",
        "lefaso.net": "Lefaso.net",
        "faso presse": "FasoPresse",
        "fasopresse": "FasoPresse",
        "sidwaya": "Sidwaya",
        "aib": "AIB",
        "lobservateur": "L'Observateur Paalga",
        "l'observateur": "L'Observateur Paalga",
        "observateur paalga": "L'Observateur Paalga",
        "rtb": "RTB",
        "bf1": "BF1",
        "omega": "Omega Radio",
        "omega radio": "Omega Radio",
        "naim toure": "Naim Touré",
        "naim touré": "Naim Touré"
    }

    normalized = name_mapping.get(media_name.lower(), media_name)
    return normalized