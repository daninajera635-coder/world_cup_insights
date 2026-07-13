import pandas as pd
import numpy as np


class ProcesadorEDA:
    def __init__(self, df):
        self.df = df.copy()

    def limpieza_datos(self):
        """Limpia los datos, eliminando nulos y convirtiendo fechas."""
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df.dropna(subset=['home_score', 'away_score'], inplace=True)
        return self.df

    def crear_columnas_derivadas(self):
        """Crea columnas de año, total de goles, diferencia y resultado."""
        self.df['year'] = self.df['date'].dt.year
        self.df['total_goals'] = self.df['home_score'] + self.df['away_score']
        self.df['goal_diff'] = self.df['home_score'] - self.df['away_score']

        # Definir ganador
        self.df['winner'] = np.where(self.df['home_score'] > self.df['away_score'], 'Local',
                                     np.where(self.df['away_score'] > self.df['home_score'], 'Visitante', 'Empate'))
        return self.df

    def resumen_descriptivo(self):
        """Retorna estadísticas descriptivas básicas."""
        return self.df[['home_score', 'away_score', 'total_goals']].describe()

    def matriz_correlacion(self):
        """Calcula la matriz de correlación para variables numéricas."""
        return self.df[['home_score', 'away_score', 'total_goals', 'goal_diff']].corr()