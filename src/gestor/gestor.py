import pandas as pd

class GestorPartidos:
    def __init__(self, df):
        self.df = df

    def get_partido(self, id_partido):
        """Retorna un partido específico por índice."""
        return self.df.loc[id_partido]

    def get_por_equipo(self, equipo):
        """Retorna todos los partidos donde participó un equipo (local o visitante)."""
        return self.df[(self.df['home_team'] == equipo) | (self.df['away_team'] == equipo)]

    def get_por_anio(self, anio):
        """Retorna partidos de un año específico."""
        # Aseguramos que la columna date sea datetime
        self.df['date'] = pd.to_datetime(self.df['date'])
        return self.df[self.df['date'].dt.year == anio]

    def get_por_sede(self, pais):
        """Retorna partidos jugados en un país sede."""
        return self.df[self.df['country'] == pais]

    def ventaja_local(self):
        """Retorna estadísticas simples de ventaja de local."""
        total = len(self.df)
        locales_ganan = len(self.df[self.df['home_score'] > self.df['away_score']])
        return {"total_partidos": total, "victorias_local": locales_ganan, "porcentaje": (locales_ganan/total)*100}