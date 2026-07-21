"""
World Cup Insights - Punto de entrada del proyecto.

Ejecuta el flujo completo del sistema:
    1. Ingesta      -> descarga el CSV publico y filtra la FIFA World Cup
    2. EDA          -> limpia los datos y crea las columnas derivadas
    3. Persistencia -> guarda el dataset procesado en data/processed/
    4. Consultas    -> demuestra los metodos de GestorPartidos

Uso:
    python main.py
"""

import os

from src.ingesta.cargador import CargadorDatos
from src.gestor.gestor import GestorPartidos
from src.eda.procesador import ProcesadorEDA

# Directorio donde vive este archivo. Se usa para construir rutas absolutas y que
# el proyecto corra igual sin importar desde donde se invoque el script.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_RAW = os.path.join(BASE_DIR, "data", "raw", "partidos-mundial.csv")
RUTA_PROCESSED = os.path.join(BASE_DIR, "data", "processed", "partidos-mundial-procesado.csv")


def separador(titulo):
    """Imprime un encabezado para que la salida en consola sea legible."""
    print("\n" + "=" * 60)
    print(titulo)
    print("=" * 60)


def main():
    # ------------------------------------------------------------------
    # 1. Ingesta de datos
    # ------------------------------------------------------------------
    separador("1. INGESTA DE DATOS")
    cargador = CargadorDatos(ruta_raw=RUTA_RAW, ruta_processed=RUTA_PROCESSED)
    # obtener_datos() reutiliza el CSV local si ya fue descargado; solo baja de
    # internet cuando el archivo no existe. Asi el proyecto corre en la revision
    # aunque no haya conexion.
    df_raw = cargador.obtener_datos()
    print(f"Partidos de Copa Mundial encontrados: {len(df_raw)}")

    # ------------------------------------------------------------------
    # 2. Procesamiento EDA: limpieza y columnas derivadas
    # ------------------------------------------------------------------
    separador("2. PROCESAMIENTO EDA")
    procesador = ProcesadorEDA(df_raw)
    procesador.limpieza_datos()
    df_final = procesador.crear_columnas_derivadas()
    print(f"Dataset procesado: {len(df_final)} filas, {len(df_final.columns)} columnas")

    print("\nResumen descriptivo:")
    print(procesador.resumen_descriptivo())

    print("\nMatriz de correlacion:")
    print(procesador.matriz_correlacion())

    # ------------------------------------------------------------------
    # 3. Persistencia del dataset procesado
    # ------------------------------------------------------------------
    separador("3. PERSISTENCIA")
    cargador.guardar_procesado(df_final)

    # ------------------------------------------------------------------
    # 4. Consultas sobre los datos
    # ------------------------------------------------------------------
    separador("4. CONSULTAS")
    gestor = GestorPartidos(df_final)

    partidos_cr = gestor.get_por_equipo("Costa Rica")
    print(f"Partidos de Costa Rica: {len(partidos_cr)}")

    partidos_2022 = gestor.get_por_anio(2022)
    print(f"Partidos del Mundial 2022: {len(partidos_2022)}")

    partidos_brasil = gestor.get_por_sede("Brazil")
    print(f"Partidos jugados en Brasil: {len(partidos_brasil)}")

    ventaja = gestor.ventaja_local()
    print(
        f"Ventaja de local: {ventaja['victorias_local']} de {ventaja['total_partidos']} "
        f"partidos ({ventaja['porcentaje']:.1f}%)"
    )

    separador("PROCESO COMPLETADO EXITOSAMENTE")


if __name__ == "__main__":
    main()
