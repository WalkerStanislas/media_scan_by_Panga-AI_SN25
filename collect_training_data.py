"""
Script pour collecter des données d'entraînement depuis tous les médias
Exécute les scrapers de training pour collecter des articles avec labels normalisés
"""
import sys
import argparse
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Ajouter le répertoire parent au path
sys.path.append(str(Path(__file__).parent))

from config.label_mapping import get_label_distribution, STANDARD_LABELS


def run_training_scraper(scraper_name, max_pages=10):
    """
    Exécute un scraper de training spécifique

    Args:
        scraper_name: Nom du scraper (ex: 'burkina24', 'lefaso')
        max_pages: Nombre de pages max à scraper
    """
    scraper_file = f"scrapers/{scraper_name}_training_scraper.py"
    scraper_path = Path(__file__).parent / scraper_file

    if not scraper_path.exists():
        print(f"❌ Scraper {scraper_name} non trouvé: {scraper_path}")
        return False

    print(f"\n{'='*60}")
    print(f"🚀 Démarrage du scraper: {scraper_name.upper()}")
    print(f"{'='*60}")

    try:
        # Exécuter le scraper avec subprocess
        result = subprocess.run(
            [sys.executable, str(scraper_path), '--max-pages', str(max_pages)],
            capture_output=True,
            text=True,
            timeout=3600  # Timeout de 1 heure
        )

        print(result.stdout)

        if result.returncode == 0:
            print(f"✅ Scraper {scraper_name} terminé avec succès")
            return True
        else:
            print(f"❌ Erreur dans le scraper {scraper_name}")
            print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print(f"⏱️ Timeout du scraper {scraper_name}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de l'exécution du scraper {scraper_name}: {e}")
        return False


def analyze_training_data():
    """
    Analyse les données d'entraînement collectées
    Affiche les statistiques par média et par label
    """
    train_data_dir = Path(__file__).parent / "train_data"

    if not train_data_dir.exists():
        print("❌ Dossier train_data non trouvé")
        return

    print(f"\n{'='*60}")
    print(f"📊 ANALYSE DES DONNÉES D'ENTRAÎNEMENT")
    print(f"{'='*60}\n")

    all_articles = []
    stats_by_media = {}

    # Parcourir tous les fichiers JSON dans train_data
    for json_file in train_data_dir.glob("*_training_data.json"):
        media_name = json_file.stem.replace('_training_data', '')

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)

            if not articles:
                print(f"⚠️  {media_name}: Aucune donnée")
                continue

            all_articles.extend(articles)

            # Statistiques par média
            label_dist = get_label_distribution(articles)
            stats_by_media[media_name] = {
                'total': len(articles),
                'labels': label_dist
            }

            print(f"📰 {media_name.upper()}")
            print(f"   Total articles: {len(articles)}")
            print(f"   Distribution des labels:")
            for label in STANDARD_LABELS:
                count = label_dist.get(label, 0)
                if count > 0:
                    percentage = (count / len(articles)) * 100
                    print(f"      - {label}: {count} ({percentage:.1f}%)")
            print()

        except Exception as e:
            print(f"❌ Erreur lors de l'analyse de {json_file}: {e}")

    # Statistiques globales
    if all_articles:
        print(f"\n{'='*60}")
        print(f"📈 STATISTIQUES GLOBALES")
        print(f"{'='*60}\n")
        print(f"Total articles collectés: {len(all_articles)}")
        print(f"Nombre de médias: {len(stats_by_media)}")

        # Distribution globale
        global_dist = get_label_distribution(all_articles)
        print(f"\nDistribution globale des labels:")
        for label in STANDARD_LABELS:
            count = global_dist.get(label, 0)
            if count > 0:
                percentage = (count / len(all_articles)) * 100
                print(f"   - {label}: {count} ({percentage:.1f}%)")

        # Vérifier l'équilibre des classes
        print(f"\n🎯 ÉQUILIBRE DES CLASSES:")
        label_counts = [global_dist[label] for label in STANDARD_LABELS if global_dist[label] > 0]
        if label_counts:
            min_count = min(label_counts)
            max_count = max(label_counts)
            ratio = max_count / min_count if min_count > 0 else float('inf')

            if ratio < 3:
                print("   ✅ Classes relativement équilibrées")
            elif ratio < 5:
                print("   ⚠️  Déséquilibre modéré des classes")
            else:
                print("   ❌ Déséquilibre important des classes")
            print(f"   Ratio max/min: {ratio:.2f}")

    print(f"\n{'='*60}\n")


def merge_training_data(output_file="train_data/merged_training_data.json"):
    """
    Fusionne toutes les données d'entraînement en un seul fichier
    """
    train_data_dir = Path(__file__).parent / "train_data"

    if not train_data_dir.exists():
        print("❌ Dossier train_data non trouvé")
        return

    print(f"\n{'='*60}")
    print(f"🔀 FUSION DES DONNÉES D'ENTRAÎNEMENT")
    print(f"{'='*60}\n")

    all_data = []

    # Parcourir tous les fichiers (sauf le merged)
    for json_file in train_data_dir.glob("*_training_data.json"):
        if "merged" in json_file.name:
            continue

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_data.extend(data)
                print(f"✅ Chargé {len(data)} articles depuis {json_file.name}")
        except Exception as e:
            print(f"❌ Erreur lors du chargement de {json_file}: {e}")

    # Sauvegarder les données fusionnées
    output_path = Path(__file__).parent / output_file

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)

        print(f"\n✅ {len(all_data)} articles fusionnés dans: {output_file}")

    except Exception as e:
        print(f"❌ Erreur lors de la sauvegarde: {e}")


def main():
    parser = argparse.ArgumentParser(
        description='Collecte de données d\'entraînement pour le modèle de classification'
    )

    parser.add_argument(
        '--scrapers',
        nargs='+',
        default=['burkina24', 'lefaso'],
        help='Liste des scrapers à exécuter (ex: burkina24 lefaso)'
    )

    parser.add_argument(
        '--max-pages',
        type=int,
        default=10,
        help='Nombre maximum de pages par catégorie/rubrique (défaut: 10)'
    )

    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Analyser uniquement les données existantes sans scraper'
    )

    parser.add_argument(
        '--merge',
        action='store_true',
        help='Fusionner toutes les données en un seul fichier'
    )

    args = parser.parse_args()

    print(f"""
╔══════════════════════════════════════════════════════════╗
║     COLLECTE DE DONNÉES D'ENTRAÎNEMENT - MÉDIA SCAN      ║
╚══════════════════════════════════════════════════════════╝

Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Scrapers: {', '.join(args.scrapers)}
Pages max: {args.max_pages}
    """)

    # Mode analyse seule
    if args.analyze_only:
        analyze_training_data()
        if args.merge:
            merge_training_data()
        return

    # Exécuter les scrapers
    success_count = 0
    total_scrapers = len(args.scrapers)

    for scraper in args.scrapers:
        if run_training_scraper(scraper, args.max_pages):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ")
    print(f"{'='*60}")
    print(f"Scrapers exécutés: {success_count}/{total_scrapers}")
    print(f"Taux de réussite: {(success_count/total_scrapers)*100:.1f}%")

    # Analyser les résultats
    analyze_training_data()

    # Fusionner si demandé
    if args.merge:
        merge_training_data()

    print(f"\n✅ Collecte terminée!")
    print(f"📁 Données dans: train_data/")


if __name__ == "__main__":
    main()