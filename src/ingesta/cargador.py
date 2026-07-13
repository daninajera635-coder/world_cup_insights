import pandas as pd
import os


class CargadorDatos:
    def __init__(self, url):
        self.url = url
        self.raw_path = 'data/raw/partidos-mundial.csv'
        self.processed_path = 'data/processed/partidos-mundial-limpios.csv'

    def descargar_y_filtrar(self):
        """Descarga el CSV y filtra solo los partidos de la Copa Mundial."""
        print("Descargando datos...")
        df = pd.read_csv(self.url)

        # Filtramos por el torneo solicitado
        df_mundial = df[df['tournament'] == 'FIFA World Cup'].copy()

        # Aseguramos que la carpeta exista antes de guardar
        os.makedirs(os.path.dirname(self.raw_path), exist_ok=True)

        # Guardamos el archivo raw
        df_mundial.to_csv(self.raw_path, index=False)
        print(f"Datos filtrados guardados en {self.raw_path}")
        return df_mundial

    def guardar_procesado(self, df):
        """Guarda el dataset ya procesado para su uso en EDA."""
        os.makedirs(os.path.dirname(self.processed_path), exist_ok=True)
        df.to_csv(self.processed_path, index=False)
        print(f"Dataset procesado guardado en {self.processed_path}")