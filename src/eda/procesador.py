<<<<<<< Updated upstream
=======
"""Modulo EDA: limpieza, columnas derivadas y estadistica descriptiva."""

import numpy as np
import pandas as pd


class ProcesadorEDA:
    """
    Realiza el analisis exploratorio sobre los partidos de Mundial.

    Trabaja siempre sobre una copia interna del DataFrame, de modo que el
    dataset original que entrega CargadorDatos nunca se altera.
    """

    COLUMNAS_NUMERICAS = ["home_score", "away_score", "total_goals", "goal_diff"]

    def __init__(self, df):
        self.df = df.copy()

    # ------------------------------------------------------------------
    # Limpieza
    # ------------------------------------------------------------------
    def limpieza_datos(self):
        """
        Deja el DataFrame listo para analizar:
            - convierte 'date' a datetime
            - descarta partidos sin marcador
            - elimina duplicados exactos
            - normaliza los nombres de equipos y sedes (espacios sobrantes)
            - convierte los marcadores a entero
        """
        self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

        # Un partido sin fecha o sin marcador no aporta al analisis.
        self.df = self.df.dropna(subset=["date", "home_score", "away_score"])

        self.df = self.df.drop_duplicates()

        for columna in ["home_team", "away_team", "city", "country"]:
            if columna in self.df.columns:
                self.df[columna] = self.df[columna].str.strip()

        # Los marcadores llegan como float por los NaN del dataset completo.
        self.df["home_score"] = self.df["home_score"].astype(int)
        self.df["away_score"] = self.df["away_score"].astype(int)

        self.df = self.df.reset_index(drop=True)
        return self.df

    # ------------------------------------------------------------------
    # Columnas derivadas
    # ------------------------------------------------------------------
    def crear_columnas_derivadas(self):
        """Crea las columnas de anio, total de goles, diferencia y ganador."""
        self.df["year"] = self.df["date"].dt.year
        self.df["total_goals"] = self.df["home_score"] + self.df["away_score"]
        self.df["goal_diff"] = self.df["home_score"] - self.df["away_score"]

        self.df["winner"] = np.where(
            self.df["home_score"] > self.df["away_score"], "Local",
            np.where(self.df["away_score"] > self.df["home_score"], "Visitante", "Empate"),
        )

        # Columnas de apoyo para agrupaciones y graficos posteriores.
        self.df["decada"] = (self.df["year"] // 10) * 10
        self.df["es_empate"] = self.df["winner"] == "Empate"

        return self.df

    # ------------------------------------------------------------------
    # Estadistica descriptiva
    # ------------------------------------------------------------------
    def resumen_descriptivo(self):
        """Retorna estadisticas descriptivas de las variables numericas."""
        columnas = [c for c in self.COLUMNAS_NUMERICAS if c in self.df.columns]
        return self.df[columnas].describe()

    def matriz_correlacion(self):
        """Calcula la matriz de correlacion entre las variables numericas."""
        columnas = [c for c in self.COLUMNAS_NUMERICAS if c in self.df.columns]
        return self.df[columnas].corr()

    def reporte_nulos(self):
        """Cantidad y porcentaje de valores nulos por columna."""
        nulos = self.df.isnull().sum()
        return pd.DataFrame({
            "nulos": nulos,
            "porcentaje": (nulos / len(self.df) * 100).round(2),
        })

    # ------------------------------------------------------------------
    # Analisis avanzado
    # ------------------------------------------------------------------
    def detectar_outliers(self, columna="total_goals"):
        """
        Detecta valores atipicos con el metodo del rango intercuartilico (IQR).

        En este dataset los outliers no son errores: son las goleadas historicas,
        que resultan justamente los partidos mas interesantes de mirar.
        """
        if columna not in self.df.columns:
            raise ValueError(f"La columna '{columna}' no existe en el DataFrame.")

        q1 = self.df[columna].quantile(0.25)
        q3 = self.df[columna].quantile(0.75)
        iqr = q3 - q1

        limite_inferior = q1 - 1.5 * iqr
        limite_superior = q3 + 1.5 * iqr

        outliers = self.df[
            (self.df[columna] < limite_inferior) | (self.df[columna] > limite_superior)
        ]

        return {
            "columna": columna,
            "q1": float(q1),
            "q3": float(q3),
            "iqr": float(iqr),
            "limite_inferior": float(limite_inferior),
            "limite_superior": float(limite_superior),
            "cantidad_outliers": len(outliers),
            "outliers": outliers.sort_values(columna, ascending=False),
        }

    def agrupar_por_edicion(self):
        """Resumen estadistico de cada Mundial: partidos, goles y resultados."""
        resumen = self.df.groupby("year").agg(
            partidos=("total_goals", "count"),
            goles_totales=("total_goals", "sum"),
            promedio_goles=("total_goals", "mean"),
            max_goles_partido=("total_goals", "max"),
            empates=("es_empate", "sum"),
        )
        resumen["porcentaje_empates"] = (
            resumen["empates"] / resumen["partidos"] * 100
        ).round(1)
        return resumen.round(2)

    def agrupar_por_decada(self):
        """Evolucion del promedio de goles por decada."""
        return self.df.groupby("decada").agg(
            partidos=("total_goals", "count"),
            promedio_goles=("total_goals", "mean"),
        ).round(2)

    def distribucion_resultados(self):
        """Reparto global entre victorias de local, visitante y empates."""
        conteo = self.df["winner"].value_counts()
        return pd.DataFrame({
            "cantidad": conteo,
            "porcentaje": (conteo / len(self.df) * 100).round(2),
        })
>>>>>>> Stashed changes
