"""
Module utilitaire pour charger et traiter les données du dashboard
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import Dict, List, Tuple

class DataLoader:
    """Classe pour charger et traiter les données du dashboard"""

    def __init__(self, data_dir: str = "data/processed"):
        """
        Initialise le DataLoader

        Args:
            data_dir: Chemin vers le répertoire des données traitées
        """
        self.data_dir = Path(data_dir)
        self.articles_df = None
        self.medias_df = None

    def load_data(self, filename: str = "sample_data.json") -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Charge les données depuis un fichier JSON

        Args:
            filename: Nom du fichier à charger

        Returns:
            Tuple de (articles_df, medias_df)
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            raise FileNotFoundError(f"Le fichier {filepath} n'existe pas")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convertir en DataFrames
        self.articles_df = pd.DataFrame(data.get('articles', []))
        self.medias_df = pd.DataFrame(data.get('medias', []))

        # Convertir les dates
        if not self.articles_df.empty and 'date' in self.articles_df.columns:
            self.articles_df['date'] = pd.to_datetime(self.articles_df['date'])

        return self.articles_df, self.medias_df

    def get_global_stats(self) -> Dict:
        """
        Calcule les statistiques globales

        Returns:
            Dictionnaire avec les statistiques
        """
        if self.articles_df is None or self.articles_df.empty:
            return {}

        # Extraire les métriques d'engagement
        total_likes = self.articles_df['engagement'].apply(lambda x: x.get('likes', 0)).sum()
        total_partages = self.articles_df['engagement'].apply(lambda x: x.get('partages', 0)).sum()
        total_commentaires = self.articles_df['engagement'].apply(lambda x: x.get('commentaires', 0)).sum()

        stats = {
            'total_articles': len(self.articles_df),
            'total_medias': len(self.medias_df) if self.medias_df is not None else 0,
            'total_engagement': total_likes + total_partages + total_commentaires,
            'total_likes': total_likes,
            'total_partages': total_partages,
            'total_commentaires': total_commentaires,
            'articles_sensibles': len(self.articles_df[self.articles_df['sensible'] == True]),
            'taux_sensible': (len(self.articles_df[self.articles_df['sensible'] == True]) / len(self.articles_df) * 100) if len(self.articles_df) > 0 else 0
        }

        return stats

    def get_articles_by_category(self) -> pd.DataFrame:
        """
        Groupe les articles par catégorie

        Returns:
            DataFrame avec le nombre d'articles par catégorie
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        category_stats = self.articles_df.groupby('categorie').agg({
            'id': 'count',
            'engagement': lambda x: sum(e.get('likes', 0) + e.get('partages', 0) + e.get('commentaires', 0) for e in x)
        }).reset_index()

        category_stats.columns = ['Catégorie', 'Nombre d\'articles', 'Engagement total']
        category_stats = category_stats.sort_values('Nombre d\'articles', ascending=False)

        return category_stats

    def get_articles_by_media(self) -> pd.DataFrame:
        """
        Groupe les articles par média

        Returns:
            DataFrame avec le nombre d'articles par média
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        media_stats = self.articles_df.groupby('media').agg({
            'id': 'count',
            'engagement': lambda x: sum(e.get('likes', 0) + e.get('partages', 0) + e.get('commentaires', 0) for e in x)
        }).reset_index()

        media_stats.columns = ['Média', 'Nombre d\'articles', 'Engagement total']
        media_stats = media_stats.sort_values('Engagement total', ascending=False)

        return media_stats

    def get_timeline_data(self, days: int = 30) -> pd.DataFrame:
        """
        Obtient les données temporelles pour les graphiques

        Args:
            days: Nombre de jours à afficher

        Returns:
            DataFrame avec les articles par jour
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        # Filtrer les derniers jours
        end_date = self.articles_df['date'].max()
        start_date = end_date - timedelta(days=days)

        filtered_df = self.articles_df[self.articles_df['date'] >= start_date].copy()

        # Grouper par date
        timeline = filtered_df.groupby(filtered_df['date'].dt.date).agg({
            'id': 'count'
        }).reset_index()

        timeline.columns = ['Date', 'Nombre d\'articles']

        return timeline

    def get_timeline_data_by_media(self, days: int = 30, selected_medias: List[str] = None) -> pd.DataFrame:
        """
        Obtient les données temporelles pour les graphiques avec détail par média

        Args:
            days: Nombre de jours à afficher
            selected_medias: Liste des médias à afficher (None = tous les médias)

        Returns:
            DataFrame avec les articles par jour et par média
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        # Filtrer les derniers jours
        end_date = self.articles_df['date'].max()
        start_date = end_date - timedelta(days=days)

        filtered_df = self.articles_df[self.articles_df['date'] >= start_date].copy()

        # Filtrer par médias sélectionnés si spécifié
        if selected_medias is not None and len(selected_medias) > 0:
            filtered_df = filtered_df[filtered_df['media'].isin(selected_medias)]

        if filtered_df.empty:
            return pd.DataFrame()

        # Grouper par date et média
        timeline = filtered_df.groupby([filtered_df['date'].dt.date, 'media']).agg({
            'id': 'count'
        }).reset_index()

        timeline.columns = ['Date', 'Média', 'Nombre d\'articles']

        return timeline

    def get_sensitive_articles(self, min_toxicity: float = 0.3) -> pd.DataFrame:
        """
        Obtient les articles sensibles

        Args:
            min_toxicity: Score de toxicité minimum

        Returns:
            DataFrame avec les articles sensibles
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        sensitive = self.articles_df[
            (self.articles_df['sensible'] == True) |
            (self.articles_df['toxicite_score'] >= min_toxicity)
        ].copy()

        # Sélectionner les colonnes pertinentes
        if not sensitive.empty:
            sensitive = sensitive[['id', 'media', 'titre', 'date', 'categorie', 'toxicite_score', 'url']]
            sensitive = sensitive.sort_values('toxicite_score', ascending=False)

        return sensitive

    def get_top_articles(self, n: int = 10, metric: str = 'engagement') -> pd.DataFrame:
        """
        Obtient les articles les plus performants

        Args:
            n: Nombre d'articles à retourner
            metric: Métrique à utiliser ('engagement', 'likes', 'partages', 'commentaires')

        Returns:
            DataFrame avec les top articles
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        df = self.articles_df.copy()

        # Calculer la métrique
        if metric == 'engagement':
            df['score'] = df['engagement'].apply(
                lambda x: x.get('likes', 0) + x.get('partages', 0) + x.get('commentaires', 0)
            )
        else:
            df['score'] = df['engagement'].apply(lambda x: x.get(metric, 0))

        # Trier et sélectionner le top
        top = df.nlargest(n, 'score')[['id', 'media', 'titre', 'date', 'categorie', 'score', 'url']]

        return top

    def get_category_distribution(self) -> Dict[str, int]:
        """
        Obtient la distribution des catégories

        Returns:
            Dictionnaire {catégorie: nombre d'articles}
        """
        if self.articles_df is None or self.articles_df.empty:
            return {}

        return self.articles_df['categorie'].value_counts().to_dict()

    def get_media_ranking(self) -> pd.DataFrame:
        """
        Obtient le classement des médias

        Returns:
            DataFrame avec le classement des médias
        """
        if self.medias_df is None or self.medias_df.empty:
            return pd.DataFrame()

        ranking = self.medias_df.sort_values('score_influence', ascending=False).copy()

        return ranking

    def get_engagement_by_category(self) -> pd.DataFrame:
        """
        Calcule l'engagement par catégorie

        Returns:
            DataFrame avec l'engagement par catégorie
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        df = self.articles_df.copy()

        # Extraire les métriques d'engagement
        df['likes'] = df['engagement'].apply(lambda x: x.get('likes', 0))
        df['partages'] = df['engagement'].apply(lambda x: x.get('partages', 0))
        df['commentaires'] = df['engagement'].apply(lambda x: x.get('commentaires', 0))
        df['total_engagement'] = df['likes'] + df['partages'] + df['commentaires']

        # Grouper par catégorie
        engagement = df.groupby('categorie').agg({
            'likes': 'sum',
            'partages': 'sum',
            'commentaires': 'sum',
            'total_engagement': 'sum'
        }).reset_index()

        engagement = engagement.sort_values('total_engagement', ascending=False)

        return engagement

    def analyze_suspicious_comments(self, article: Dict) -> Dict:
        """
        Analyse les commentaires d'un article pour détecter les commentaires suspects

        Args:
            article: Dictionnaire représentant un article

        Returns:
            Dictionnaire avec les informations sur les commentaires suspects
        """
        comments_sensibles = article.get('comments_sensibles', None)

        if comments_sensibles is None or len(comments_sensibles) == 0:
            return {
                'has_alert': False,
                'alert_type': None,
                'nb_comments_sensibles': 0,
                'nb_highly_toxic': 0,
                'max_toxicity': 0.0
            }

        # Compter les commentaires sensibles et très toxiques
        nb_sensibles = sum(1 for c in comments_sensibles if c.get('comment_sensible', False))
        nb_highly_toxic = sum(1 for c in comments_sensibles if c.get('toxicite_score', 0) > 0.8)
        max_toxicity = max([c.get('toxicite_score', 0) for c in comments_sensibles], default=0.0)

        # Logique d'alerte selon les critères :
        # 1. Au moins un commentaire sensible (True) ET/OU avec toxicité > 0.8
        # 2. Plus de 10 commentaires suspects au total

        has_critical_comment = nb_sensibles > 0 or nb_highly_toxic > 0
        has_mass_suspects = len(comments_sensibles) > 10

        alert_type = None
        if has_critical_comment and has_mass_suspects:
            alert_type = 'critical_mass'  # Les deux conditions
        elif has_critical_comment:
            alert_type = 'critical'  # Commentaire(s) très toxique(s) ou sensible(s)
        elif has_mass_suspects:
            alert_type = 'mass'  # Volume élevé de commentaires suspects

        return {
            'has_alert': alert_type is not None,
            'alert_type': alert_type,
            'nb_comments_sensibles': nb_sensibles,
            'nb_highly_toxic': nb_highly_toxic,
            'nb_total_comments': len(comments_sensibles),
            'max_toxicity': max_toxicity
        }

    def get_articles_with_suspicious_comments(self) -> pd.DataFrame:
        """
        Obtient tous les articles avec des commentaires suspects déclenchant une alerte

        Returns:
            DataFrame avec les articles ayant des alertes de commentaires
        """
        if self.articles_df is None or self.articles_df.empty:
            return pd.DataFrame()

        articles_with_alerts = []

        for idx, row in self.articles_df.iterrows():
            article_dict = row.to_dict()
            alert_info = self.analyze_suspicious_comments(article_dict)

            if alert_info['has_alert']:
                article_info = {
                    'id': row['id'],
                    'media': row['media'],
                    'titre': row['titre'],
                    'date': row['date'],
                    'categorie': row['categorie'],
                    'url': row['url'],
                    'alert_type': alert_info['alert_type'],
                    'nb_comments_sensibles': alert_info['nb_comments_sensibles'],
                    'nb_highly_toxic': alert_info['nb_highly_toxic'],
                    'nb_total_comments': alert_info['nb_total_comments'],
                    'max_toxicity': alert_info['max_toxicity'],
                    'comments_sensibles': row.get('comments_sensibles', [])
                }
                articles_with_alerts.append(article_info)

        if not articles_with_alerts:
            return pd.DataFrame()

        df_alerts = pd.DataFrame(articles_with_alerts)
        # Trier par niveau de criticité (critical_mass > critical > mass)
        df_alerts['alert_priority'] = df_alerts['alert_type'].map({
            'critical_mass': 3,
            'critical': 2,
            'mass': 1
        })
        df_alerts = df_alerts.sort_values(['alert_priority', 'max_toxicity'], ascending=[False, False])
        df_alerts = df_alerts.drop('alert_priority', axis=1)

        return df_alerts

    def get_comments_stats(self) -> Dict:
        """
        Calcule les statistiques globales sur les commentaires suspects

        Returns:
            Dictionnaire avec les statistiques
        """
        if self.articles_df is None or self.articles_df.empty:
            return {}

        total_articles_with_comments = 0
        total_alerts = 0
        critical_alerts = 0
        mass_alerts = 0
        critical_mass_alerts = 0

        for idx, row in self.articles_df.iterrows():
            article_dict = row.to_dict()
            comments = article_dict.get('comments_sensibles', None)

            if comments is not None and len(comments) > 0:
                total_articles_with_comments += 1

            alert_info = self.analyze_suspicious_comments(article_dict)
            if alert_info['has_alert']:
                total_alerts += 1
                if alert_info['alert_type'] == 'critical':
                    critical_alerts += 1
                elif alert_info['alert_type'] == 'mass':
                    mass_alerts += 1
                elif alert_info['alert_type'] == 'critical_mass':
                    critical_mass_alerts += 1

        return {
            'total_articles_with_comments': total_articles_with_comments,
            'total_alerts': total_alerts,
            'critical_alerts': critical_alerts,
            'mass_alerts': mass_alerts,
            'critical_mass_alerts': critical_mass_alerts
        }

    def export_to_dict(self) -> Dict:
        """
        Exporte toutes les données en dictionnaire pour les rapports

        Returns:
            Dictionnaire avec toutes les statistiques
        """
        def convert_to_python_types(obj):
            """Convertit les types numpy et pandas en types Python natifs"""
            import numpy as np
            if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                np.int16, np.int32, np.int64, np.uint8,
                np.uint16, np.uint32, np.uint64)):
                return int(obj)
            elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (pd.Timestamp, pd.DatetimeTZDtype)):
                return obj.isoformat() if hasattr(obj, 'isoformat') else str(obj)
            elif isinstance(obj, dict):
                return {k: convert_to_python_types(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_python_types(i) for i in obj]
            return obj

        data = {
            'global_stats': self.get_global_stats(),
            'category_distribution': self.get_category_distribution(),
            'articles_by_category': self.get_articles_by_category().to_dict('records'),
            'articles_by_media': self.get_articles_by_media().to_dict('records'),
            'media_ranking': self.get_media_ranking().to_dict('records'),
            'sensitive_articles': self.get_sensitive_articles().to_dict('records'),
            'top_articles': self.get_top_articles().to_dict('records')
        }

        return convert_to_python_types(data)