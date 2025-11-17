"""
Module pour générer des rapports PDF et Excel
"""
import pandas as pd
from datetime import datetime
from typing import Dict
from io import BytesIO
try:
    from fpdf import FPDF
except ImportError:
    # fpdf2 est installé comme 'fpdf2' mais s'importe comme 'fpdf'
    # Si l'import échoue, on définit une classe factice
    FPDF = None
import json


class ReportGenerator:
    """Classe pour générer des rapports au format PDF et Excel"""

    def __init__(self, data_loader):
        """
        Initialise le générateur de rapports

        Args:
            data_loader: Instance de DataLoader avec les données chargées
        """
        self.data_loader = data_loader

    def generate_excel_report(self) -> BytesIO:
        """
        Génère un rapport Excel complet

        Returns:
            BytesIO contenant le fichier Excel
        """
        output = BytesIO()

        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Onglet 1: Statistiques globales
            global_stats = pd.DataFrame([self.data_loader.get_global_stats()])
            global_stats.to_excel(writer, sheet_name='Statistiques Globales', index=False)

            # Onglet 2: Classement des médias
            media_ranking = self.data_loader.get_media_ranking()
            if not media_ranking.empty:
                media_ranking.to_excel(writer, sheet_name='Classement Médias', index=False)

            # Onglet 3: Articles par catégorie
            category_stats = self.data_loader.get_articles_by_category()
            if not category_stats.empty:
                category_stats.to_excel(writer, sheet_name='Articles par Catégorie', index=False)

            # Onglet 4: Articles par média
            media_stats = self.data_loader.get_articles_by_media()
            if not media_stats.empty:
                media_stats.to_excel(writer, sheet_name='Articles par Média', index=False)

            # Onglet 5: Engagement par catégorie
            engagement = self.data_loader.get_engagement_by_category()
            if not engagement.empty:
                engagement.to_excel(writer, sheet_name='Engagement par Catégorie', index=False)

            # Onglet 6: Top articles
            top_articles = self.data_loader.get_top_articles(n=20)
            if not top_articles.empty:
                top_articles.to_excel(writer, sheet_name='Top Articles', index=False)

            # Onglet 7: Articles sensibles
            sensitive = self.data_loader.get_sensitive_articles()
            if not sensitive.empty:
                sensitive.to_excel(writer, sheet_name='Contenus Sensibles', index=False)

            # Onglet 8: Tous les articles
            if self.data_loader.articles_df is not None and not self.data_loader.articles_df.empty:
                # Créer une version aplatie pour Excel
                articles_export = self.data_loader.articles_df.copy()
                articles_export['likes'] = articles_export['engagement'].apply(lambda x: x.get('likes', 0))
                articles_export['partages'] = articles_export['engagement'].apply(lambda x: x.get('partages', 0))
                articles_export['commentaires'] = articles_export['engagement'].apply(lambda x: x.get('commentaires', 0))
                articles_export = articles_export.drop('engagement', axis=1)
                articles_export.to_excel(writer, sheet_name='Tous les Articles', index=False)

        output.seek(0)
        return output

    def generate_pdf_report(self) -> BytesIO:
        """
        Génère un rapport PDF

        Returns:
            BytesIO contenant le fichier PDF
        """
        if FPDF is None:
            raise ImportError("fpdf2 n'est pas installé. Installez-le avec: pip install fpdf2")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Titre
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(0, 10, 'MÉDIA-SCAN', 0, 1, 'C')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Rapport d\'Analyse des Médias Burkinabè', 0, 1, 'C')
        pdf.cell(0, 10, f'Généré le {datetime.now().strftime("%d/%m/%Y à %H:%M")}', 0, 1, 'C')
        pdf.ln(10)

        # Statistiques globales
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '1. STATISTIQUES GLOBALES', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)

        stats = self.data_loader.get_global_stats()
        if stats:
            pdf.ln(5)
            pdf.cell(0, 8, f'Total d\'articles analysés: {stats.get("total_articles", 0)}', 0, 1)
            pdf.cell(0, 8, f'Nombre de médias: {stats.get("total_medias", 0)}', 0, 1)
            pdf.cell(0, 8, f'Engagement total: {stats.get("total_engagement", 0):,}', 0, 1)
            pdf.cell(0, 8, f'  - Likes: {stats.get("total_likes", 0):,}', 0, 1)
            pdf.cell(0, 8, f'  - Partages: {stats.get("total_partages", 0):,}', 0, 1)
            pdf.cell(0, 8, f'  - Commentaires: {stats.get("total_commentaires", 0):,}', 0, 1)
            pdf.cell(0, 8, f'Articles sensibles: {stats.get("articles_sensibles", 0)} ({stats.get("taux_sensible", 0):.1f}%)', 0, 1)

        pdf.ln(10)

        # Classement des médias
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '2. CLASSEMENT DES MÉDIAS', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)

        media_ranking = self.data_loader.get_media_ranking()
        if not media_ranking.empty:
            pdf.ln(5)
            # En-têtes
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(10, 8, '#', 1)
            pdf.cell(70, 8, 'Média', 1)
            pdf.cell(35, 8, 'Articles', 1)
            pdf.cell(35, 8, 'Score', 1)
            pdf.cell(30, 8, 'Actif 90j', 1)
            pdf.ln()

            # Données
            pdf.set_font('Arial', '', 10)
            for idx, row in media_ranking.head(10).iterrows():
                pdf.cell(10, 8, str(row.get('rang', idx + 1)), 1)
                pdf.cell(70, 8, str(row.get('nom', ''))[:30], 1)
                pdf.cell(35, 8, str(row.get('nb_articles', 0)), 1)
                pdf.cell(35, 8, f"{row.get('score_influence', 0):.2f}", 1)
                pdf.cell(30, 8, 'Oui' if row.get('actif_90j', False) else 'Non', 1)
                pdf.ln()

        pdf.ln(10)

        # Distribution thématique
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '3. DISTRIBUTION THÉMATIQUE', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)

        category_stats = self.data_loader.get_articles_by_category()
        if not category_stats.empty:
            pdf.ln(5)
            # En-têtes
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(70, 8, 'Catégorie', 1)
            pdf.cell(50, 8, 'Nombre d\'articles', 1)
            pdf.cell(60, 8, 'Engagement total', 1)
            pdf.ln()

            # Données
            pdf.set_font('Arial', '', 10)
            for idx, row in category_stats.iterrows():
                pdf.cell(70, 8, str(row.get('Catégorie', '')), 1)
                pdf.cell(50, 8, str(row.get('Nombre d\'articles', 0)), 1)
                pdf.cell(60, 8, f"{row.get('Engagement total', 0):,}", 1)
                pdf.ln()

        pdf.ln(10)

        # Contenus sensibles
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '4. CONTENUS SENSIBLES', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)

        sensitive = self.data_loader.get_sensitive_articles()
        if not sensitive.empty:
            pdf.ln(5)
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 8, f'Nombre total de contenus sensibles détectés: {len(sensitive)}', 0, 1)
            pdf.ln(3)

            # Top 10 contenus sensibles
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, 'Top 10 des contenus les plus sensibles:', 0, 1)
            pdf.ln(2)

            pdf.set_font('Arial', '', 9)
            for idx, row in sensitive.head(10).iterrows():
                pdf.multi_cell(0, 6, f"- {row.get('titre', '')} ({row.get('media', '')}) - Score: {row.get('toxicite_score', 0):.2f}")
                pdf.ln(1)

        pdf.ln(10)

        # Top articles
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, '5. TOP ARTICLES (PAR ENGAGEMENT)', 0, 1, 'L')
        pdf.set_font('Arial', '', 11)

        top_articles = self.data_loader.get_top_articles(n=10)
        if not top_articles.empty:
            pdf.ln(5)
            pdf.set_font('Arial', '', 9)
            for idx, row in top_articles.iterrows():
                pdf.set_font('Arial', 'B', 9)
                pdf.multi_cell(0, 6, f"{idx + 1}. {row.get('titre', '')}")
                pdf.set_font('Arial', '', 9)
                pdf.cell(0, 5, f"   Média: {row.get('media', '')} | Catégorie: {row.get('categorie', '')} | Engagement: {row.get('score', 0):,}", 0, 1)
                pdf.ln(2)

        # Pied de page
        pdf.ln(20)
        pdf.set_font('Arial', 'I', 10)
        pdf.cell(0, 10, 'Rapport généré par MÉDIA-SCAN - CSC Burkina Faso', 0, 1, 'C')

        # Sauvegarder en BytesIO
        output = BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        output.write(pdf_content)
        output.seek(0)

        return output

    def generate_json_report(self) -> str:
        """
        Génère un rapport au format JSON

        Returns:
            String JSON avec toutes les statistiques
        """
        report_data = self.data_loader.export_to_dict()
        report_data['generated_at'] = datetime.now().isoformat()
        report_data['report_type'] = 'media_analysis'

        return json.dumps(report_data, ensure_ascii=False, indent=2)