"""Modulo de ingesta: descarga, validacion y persistencia de los datos."""

import os

import pandas as pd


class CargadorDatos:
    """
    Se encarga de traer los datos a la aplicacion y de guardarlos en disco.

    Responsabilidades:
        - Descargar el CSV publico de resultados internacionales.
        - Filtrar unicamente los partidos de la Copa Mundial de la FIFA.
        - Validar que los datos tengan la forma esperada.
        - Persistir el dataset en /data/raw y /data/processed (CSV y JSON).
    """

    URL_DATASET = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

    # Valor de la columna 'tournament' que identifica a los partidos de Mundial.
    TORNEO = "FIFA World Cup"

    # Columnas que el CSV de origen debe traer si o si.
    COLUMNAS_REQUERIDAS = [
        "date", "home_team", "away_team", "home_score",
        "away_score", "tournament", "city", "country", "neutral",
    ]

    def __init__(self, ruta_raw="data/raw/partidos-mundial.csv",
                 ruta_processed="data/processed/partidos-mundial-procesado.csv"):
        self.ruta_raw = ruta_raw
        self.ruta_processed = ruta_processed
        self.df_raw = None
        self.df_procesado = None

    # ------------------------------------------------------------------
    # Descarga e ingesta
    # ------------------------------------------------------------------
    def descargar_y_filtrar_raw(self):
        """
        Descarga el CSV publico, filtra los partidos de la FIFA World Cup
        y guarda la version raw en data/raw/partidos-mundial.csv.
        """
        print("Descargando dataset completo desde GitHub...")
        try:
            df_completo = pd.read_csv(self.URL_DATASET)
        except Exception as error:
            raise ConnectionError(
                f"No se pudo descargar el dataset desde {self.URL_DATASET}. "
                f"Revise su conexion a internet. Detalle: {error}"
            )

        self.validar_columnas(df_completo)

        print(f"Filtrando partidos de la '{self.TORNEO}'...")
        self.df_raw = df_completo[df_completo["tournament"] == self.TORNEO].copy()

        if self.df_raw.empty:
            raise ValueError(
                f"El filtro por '{self.TORNEO}' no devolvio ningun partido. "
                "Es posible que el dataset de origen haya cambiado."
            )

        self._guardar_csv(self.df_raw, self.ruta_raw)
        print(f"[OK] Archivo raw guardado exitosamente en: {self.ruta_raw}")
        return self.df_raw

    def cargar_raw_local(self):
        """
        Lee el CSV ya descargado desde data/raw/, sin salir a internet.
        Util para trabajar sin conexion o para no re-descargar en cada corrida.
        """
        if not os.path.exists(self.ruta_raw):
            raise FileNotFoundError(
                f"No existe el archivo {self.ruta_raw}. "
                "Ejecute primero descargar_y_filtrar_raw()."
            )

        self.df_raw = pd.read_csv(self.ruta_raw)
        print(f"[OK] Datos leidos desde disco: {self.ruta_raw} ({len(self.df_raw)} partidos)")
        return self.df_raw

    def obtener_datos(self, forzar_descarga=False):
        """
        Devuelve los datos raw usando la estrategia mas conveniente:
        si el archivo local existe lo reutiliza, y si no, lo descarga.

        Args:
            forzar_descarga: si es True siempre vuelve a descargar el CSV.
        """
        if forzar_descarga or not os.path.exists(self.ruta_raw):
            return self.descargar_y_filtrar_raw()
        return self.cargar_raw_local()

    # ------------------------------------------------------------------
    # Validacion
    # ------------------------------------------------------------------
    def validar_columnas(self, df):
        """Verifica que el DataFrame traiga todas las columnas requeridas."""
        faltantes = [c for c in self.COLUMNAS_REQUERIDAS if c not in df.columns]
        if faltantes:
            raise ValueError(
                f"El dataset de origen no trae las columnas esperadas: {faltantes}"
            )
        return True

    def validar_datos(self, df):
        """
        Revisa la calidad del DataFrame y devuelve un reporte con los hallazgos.
        No modifica los datos: solo informa.
        """
        reporte = {
            "total_filas": len(df),
            "filas_duplicadas": int(df.duplicated().sum()),
            "nulos_por_columna": df.isnull().sum().to_dict(),
            "marcadores_negativos": int(
                ((df["home_score"] < 0) | (df["away_score"] < 0)).sum()
            ),
        }

        if "date" in df.columns:
            fechas = pd.to_datetime(df["date"], errors="coerce")
            reporte["fechas_invalidas"] = int(fechas.isnull().sum())
            reporte["rango_fechas"] = (str(fechas.min().date()), str(fechas.max().date()))

        return reporte

    # ------------------------------------------------------------------
    # Persistencia
    # ------------------------------------------------------------------
    def guardar_procesado(self, df):
        """Guarda el DataFrame limpio y con columnas derivadas en CSV."""
        self.df_procesado = df
        self._guardar_csv(df, self.ruta_processed)
        print(f"[OK] Dataset procesado guardado exitosamente en: {self.ruta_processed}")
        return self.ruta_processed

    def guardar_procesado_json(self, ruta_json=None):
        """
        Guarda el dataset procesado tambien en JSON.
        El enunciado permite persistir en CSV y/o JSON dentro de data/processed/.
        """
        if self.df_procesado is None:
            raise ValueError("No hay dataset procesado. Llame primero a guardar_procesado().")

        if ruta_json is None:
            ruta_json = self.ruta_processed.replace(".csv", ".json")

        os.makedirs(os.path.dirname(ruta_json), exist_ok=True)
        self.df_procesado.to_json(ruta_json, orient="records", date_format="iso", indent=2)
        print(f"[OK] Dataset procesado guardado en JSON: {ruta_json}")
        return ruta_json

    def cargar_procesado(self):
        """Lee el dataset ya procesado desde data/processed/."""
        if not os.path.exists(self.ruta_processed):
            raise FileNotFoundError(
                f"No existe el archivo {self.ruta_processed}. "
                "Ejecute primero el flujo completo desde main.py."
            )

        self.df_procesado = pd.read_csv(self.ruta_processed, parse_dates=["date"])
        return self.df_procesado

    # ------------------------------------------------------------------
    # Auxiliares internos
    # ------------------------------------------------------------------
    @staticmethod
    def _guardar_csv(df, ruta):
        """Crea la carpeta destino si hace falta y escribe el CSV."""
        carpeta = os.path.dirname(ruta)
        if carpeta:
            os.makedirs(carpeta, exist_ok=True)
        df.to_csv(ruta, index=False)
