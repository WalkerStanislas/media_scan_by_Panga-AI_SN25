"""
Script pour mettre à jour les dates des articles Lefaso.net
en les récupérant directement depuis leurs URLs
"""

import json
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from pathlib import Path

def extract_date_from_lefaso_article(url):
    """
    Extrait la date de publication d'un article Lefaso.net

    Args:
        url: URL de l'article

    Returns:
        Date au format YYYY-MM-DD ou None si erreur
    """
    try:
        # Ajouter un délai pour ne pas surcharger le serveur
        time.sleep(1)

        # Récupérer la page
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Parser le HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Chercher la balise contenant la date
        # Format attendu: "Publié le dimanche 7 juillet 2024 à 22h00min"
        date_text = None

        # Méthode 1: Chercher dans les paragraphes
        for p in soup.find_all('p'):
            text = p.get_text()
            if 'Publié le' in text:
                date_text = text
                break

        if not date_text:
            print(f"   ⚠️  Date non trouvée pour {url}")
            return None

        # Extraire la date avec une regex
        # Format: "Publié le dimanche 7 juillet 2024 à 22h00min"
        # On cherche le pattern: jour mois année
        months_fr = {
            'janvier': '01', 'février': '02', 'mars': '03', 'avril': '04',
            'mai': '05', 'juin': '06', 'juillet': '07', 'août': '08',
            'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }

        # Regex pour capturer: jour mois année (et optionnellement heure)
        # Gère aussi "1er", "2ème", etc.
        pattern = r'(\d{1,2})(?:er|ème)?\s+(' + '|'.join(months_fr.keys()) + r')\s+(\d{4})(?:\s+à\s+(\d{1,2})h(\d{2}))?'
        match = re.search(pattern, date_text, re.IGNORECASE)

        if match:
            day = match.group(1).zfill(2)
            month = months_fr[match.group(2).lower()]
            year = match.group(3)
            hour = match.group(4).zfill(2) if match.group(4) else '00'
            minute = match.group(5) if match.group(5) else '00'

            # Format: YYYY-MM-DD HH:MM:SS
            date_str = f"{year}-{month}-{day} {hour}:{minute}:00"

            # Valider la date
            datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')

            return date_str
        else:
            print(f"   ⚠️  Format de date non reconnu: {date_text}")
            return None

    except requests.RequestException as e:
        print(f"   ❌ Erreur réseau pour {url}: {e}")
        return None
    except Exception as e:
        print(f"   ❌ Erreur inattendue pour {url}: {e}")
        return None


def update_lefaso_dates(input_file, output_file=None):
    """
    Met à jour les dates des articles Lefaso.net dans le fichier JSON

    Args:
        input_file: Chemin vers le fichier JSON source
        output_file: Chemin vers le fichier JSON de sortie (si None, écrase l'original)
    """
    # Charger le fichier
    print(f"📖 Chargement du fichier {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    articles = data.get('articles', [])

    # Filtrer les articles Lefaso.net
    lefaso_articles = [a for a in articles if a.get('media') == 'Lefaso.net']
    print(f"✅ {len(lefaso_articles)} articles Lefaso.net trouvés sur {len(articles)} articles au total")

    # Mettre à jour les dates
    updated_count = 0
    failed_count = 0

    print("\n🔄 Mise à jour des dates en cours...\n")

    for i, article in enumerate(lefaso_articles, 1):
        url = article.get('url', '')
        article_id = article.get('id', 'N/A')
        titre = article.get('titre', 'N/A')[:60]

        print(f"[{i}/{len(lefaso_articles)}] {titre}...")
        print(f"   URL: {url}")

        if not url:
            print(f"   ⚠️  Pas d'URL disponible")
            failed_count += 1
            continue

        # Extraire la date
        new_date = extract_date_from_lefaso_article(url)

        if new_date:
            old_date = article.get('date', 'N/A')
            article['date'] = new_date
            print(f"   ✅ Date mise à jour: {old_date} → {new_date}")
            updated_count += 1
        else:
            print(f"   ❌ Échec de la mise à jour")
            failed_count += 1

        print()

    # Sauvegarder le fichier
    output_path = output_file if output_file else input_file
    print(f"\n💾 Sauvegarde des modifications dans {output_path}...")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Terminé!")
    print(f"   📊 Statistiques:")
    print(f"      - Articles Lefaso.net: {len(lefaso_articles)}")
    print(f"      - Dates mises à jour: {updated_count}")
    print(f"      - Échecs: {failed_count}")
    print(f"      - Taux de succès: {(updated_count/len(lefaso_articles)*100):.1f}%")


if __name__ == "__main__":
    # Chemins des fichiers
    input_file = Path("data/processed/final_db1.json")

    # Optionnel: créer une sauvegarde avant modification
    backup_file = Path("data/processed/final_db1_backup.json")

    print("=" * 70)
    print("🔧 MISE À JOUR DES DATES LEFASO.NET")
    print("=" * 70)
    print()

    # Demander confirmation
    print(f"⚠️  Ce script va modifier le fichier: {input_file}")
    print(f"📦 Une sauvegarde sera créée: {backup_file}")
    print()

    response = input("Voulez-vous continuer? (o/n): ")

    if response.lower() == 'o':
        # Créer une sauvegarde
        print(f"\n📦 Création d'une sauvegarde...")
        import shutil
        shutil.copy2(input_file, backup_file)
        print(f"✅ Sauvegarde créée: {backup_file}")
        print()

        # Mettre à jour les dates
        update_lefaso_dates(input_file)
    else:
        print("\n❌ Opération annulée")