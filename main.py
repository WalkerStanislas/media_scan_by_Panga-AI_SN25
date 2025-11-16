"""
MÉDIA-SCAN - Main Entry Point
Système Intelligent d'Observation et d'Analyse des Médias au Burkina Faso
"""
import argparse
import json
from pathlib import Path
from datetime import datetime

from config.settings import RAW_DATA_DIR, PROCESSED_DATA_DIR, MEDIA_SOURCES
from database.db_manager import DatabaseManager


def scrape_all_medias(max_pages=10):
    """
    Run scrapers for all enabled media sources
    """
    print("="*60)
    print("MÉDIA-SCAN - Collecte de données")
    print("="*60)

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    # Import scrapers
    from scrapers.lefaso_scraper import LefasoScraper
    from scrapers.fasopresse_scraper import FasoPresseScraper
    from scrapers.sidwaya_scraper import SidwayaScraper
    from scrapers.lobservateur_scraper import LObservateurScraper
    from scrapers.aib_scraper import AIBScraper
    from scrapers.burkina_24_scraper import Burkina24Scraper

    process = CrawlerProcess(get_project_settings())

    # Add all enabled scrapers
    enabled_scrapers = []

    if MEDIA_SOURCES['lefaso']['enabled']:
        enabled_scrapers.append((LefasoScraper, 'Lefaso.net'))
        process.crawl(LefasoScraper, max_pages=max_pages)

    if MEDIA_SOURCES['fasopresse']['enabled']:
        enabled_scrapers.append((FasoPresseScraper, 'FasoPresse'))
        process.crawl(FasoPresseScraper, max_pages=max_pages)

    if MEDIA_SOURCES['sidwaya']['enabled']:
        enabled_scrapers.append((SidwayaScraper, 'Sidwaya'))
        process.crawl(SidwayaScraper, max_pages=max_pages)

    if MEDIA_SOURCES['observateur_paalga']['enabled']:
        enabled_scrapers.append((LObservateurScraper, "L'Observateur Paalga"))
        process.crawl(LObservateurScraper, max_pages=max_pages)
    
    if MEDIA_SOURCES['aib']['enabled']:
        enabled_scrapers.append((AIBScraper, "AIB (Agence d'Information du Burkina)"))
        process.crawl(AIBScraper, max_pages=max_pages)

    if MEDIA_SOURCES['burkina_24']['enabled']:
        enabled_scrapers.append((Burkina24Scraper, "Burkina 24"))
        process.crawl(Burkina24Scraper, max_pages=max_pages)

    print(f"\nLancement du scraping pour {len(enabled_scrapers)} médias:")
    for _, name in enabled_scrapers:
        print(f"  - {name}")

    print(f"\nPages maximum par rubrique/catégorie: {max_pages}")
    print("\nDémarrage du scraping...\n")

    try:
        process.start()
        print("\n✓ Scraping terminé avec succès!")
    except Exception as e:
        print(f"\n✗ Erreur lors du scraping: {e}")


def import_to_database():
    """
    Import scraped data from JSON files to database
    """
    print("="*60)
    print("MÉDIA-SCAN - Import des données vers la base de données")
    print("="*60)

    db = DatabaseManager()
    db.init_db()

    # Initialize media outlets in database
    for key, media_info in MEDIA_SOURCES.items():
        if media_info['enabled']:
            db.add_media(
                nom=media_info['name'],
                base_url=media_info['base_url'],
                type_media="web"
            )
            print(f"✓ Média ajouté: {media_info['name']}")

    # Import articles from JSON files
    json_files = list(RAW_DATA_DIR.glob("*.json"))
    total_imported = 0

    for json_file in json_files:
        print(f"\nImport de: {json_file.name}")

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                articles = json.load(f)

            if isinstance(articles, dict):
                articles = [articles]

            count = db.bulk_add_articles(articles)
            total_imported += count
            print(f"  ✓ {count} articles importés")

        except Exception as e:
            print(f"  ✗ Erreur lors de l'import: {e}")

    print(f"\n{'='*60}")
    print(f"TOTAL: {total_imported} articles importés dans la base de données")
    print(f"{'='*60}")

    # Update statistics
    print("\nMise à jour des statistiques...")
    for media_info in MEDIA_SOURCES.values():
        if media_info['enabled']:
            db.update_media_stats(media_info['name'])

    db.calculate_influence_scores()
    print("✓ Statistiques mises à jour")


def show_stats():
    """
    Display statistics summary
    """
    print("="*60)
    print("MÉDIA-SCAN - Statistiques")
    print("="*60)

    db = DatabaseManager()
    stats = db.get_stats_summary()

    print(f"\nMédias surveillés: {stats['total_medias']}")
    print(f"Articles collectés: {stats['total_articles']}")
    print(f"Engagement total: {stats['total_engagement']}")
    print(f"Articles récents (7 jours): {stats['recent_articles_7d']}")

    print("\nDistribution par catégorie:")
    for cat, count in sorted(stats['category_distribution'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat}: {count}")

    print("\nClassement des médias par influence:")
    medias = db.get_all_medias()
    sorted_medias = sorted(medias, key=lambda m: m.score_influence, reverse=True)

    for media in sorted_medias:
        print(f"  {media.rang}. {media.nom}")
        print(f"     Score d'influence: {media.score_influence}")
        print(f"     Articles: {media.nb_articles}")
        print(f"     Engagement: {media.engagement_total}")
        print(f"     Actif 90j: {'Oui' if media.actif_90j else 'Non'}")
        print()


def run_analysis():
    """
    Run thematic classification and content analysis
    """
    print("="*60)
    print("MÉDIA-SCAN - Analyse des contenus")
    print("="*60)

    print("\n[INFO] Module d'analyse à implémenter")
    print("  - Classification thématique (MODULE 2)")
    print("  - Détection de contenus sensibles (MODULE 5)")
    print("\nCe module sera développé dans l'étape suivante.")


def launch_dashboard():
    """
    Launch the Streamlit dashboard
    """
    import os
    import subprocess

    print("="*60)
    print("MÉDIA-SCAN - Lancement du Dashboard")
    print("="*60)

    dashboard_path = Path(__file__).parent / "dashboard" / "app.py"

    if not dashboard_path.exists():
        print(f"\n✗ Le fichier dashboard n'existe pas: {dashboard_path}")
        print("  Le dashboard sera développé dans l'étape suivante.")
        return

    print(f"\nLancement du dashboard Streamlit...")
    print(f"URL: http://localhost:8501")
    print("\nAppuyez sur Ctrl+C pour arrêter le dashboard\n")

    try:
        subprocess.run(["streamlit", "run", str(dashboard_path)])
    except KeyboardInterrupt:
        print("\n\nDashboard arrêté.")
    except Exception as e:
        print(f"\n✗ Erreur lors du lancement: {e}")


def main():
    """
    Main entry point
    """
    parser = argparse.ArgumentParser(
        description="MÉDIA-SCAN - Système d'Analyse des Médias au Burkina Faso",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  python main.py --scrape --max-pages 20     # Scraper les médias (20 pages/rubrique)
  python main.py --import                     # Importer les données scrapées
  python main.py --stats                      # Afficher les statistiques
  python main.py --analyze                    # Analyser les contenus
  python main.py --dashboard                  # Lancer le dashboard

Workflow complet:
  1. python main.py --scrape --max-pages 20
  2. python main.py --import
  3. python main.py --analyze
  4. python main.py --dashboard
        """
    )

    parser.add_argument('--scrape', action='store_true',
                        help='Lancer le scraping de tous les médias')
    parser.add_argument('--max-pages', type=int, default=10,
                        help='Nombre maximum de pages à scraper par rubrique (défaut: 10)')
    parser.add_argument('--import', dest='import_data', action='store_true',
                        help='Importer les données JSON vers la base de données')
    parser.add_argument('--stats', action='store_true',
                        help='Afficher les statistiques')
    parser.add_argument('--analyze', action='store_true',
                        help='Analyser les contenus (classification, détection)')
    parser.add_argument('--dashboard', action='store_true',
                        help='Lancer le dashboard interactif')
    parser.add_argument('--all', action='store_true',
                        help='Exécuter toutes les étapes (scrape, import, analyze)')

    args = parser.parse_args()

    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return

    print("\n" + "="*60)
    print("MÉDIA-SCAN")
    print("Système Intelligent d'Observation et d'Analyse des Médias")
    print("="*60)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

    # Execute requested operations
    if args.all or args.scrape:
        scrape_all_medias(max_pages=args.max_pages)

    if args.all or args.import_data:
        import_to_database()

    if args.all or args.analyze:
        run_analysis()

    if args.stats:
        show_stats()

    if args.dashboard:
        launch_dashboard()

    print("\n" + "="*60)
    print("Opération(s) terminée(s)")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()