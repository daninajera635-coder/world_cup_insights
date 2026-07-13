from src.ingesta.cargador import CargadorDatos


def main():
    URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

    # Instanciamos el cargador
    cargador = CargadorDatos(URL)

    # Ejecutamos la ingesta
    df = cargador.descargar_y_filtrar()

    # Mostramos los primeros resultados para verificar
    print(df.head())


if __name__ == "__main__":
    main()

from src.ingesta.cargador import CargadorDatos
from src.gestor.gestor import GestorPartidos


def main():
    URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

    # 1. Ingesta
    cargador = CargadorDatos(URL)
    df = cargador.descargar_y_filtrar()

    # 2. Gestión
    gestor = GestorPartidos(df)

    # Ejemplo de prueba: Consultar partidos de "Costa Rica"
    partidos_cr = gestor.get_por_equipo("Costa Rica")
    print(f"Partidos de Costa Rica encontrados: {len(partidos_cr)}")
    print(gestor.ventaja_local())


if __name__ == "__main__":
    main()

    from src.ingesta.cargador import CargadorDatos
    from src.gestor.gestor import GestorPartidos
    from src.eda.procesador import ProcesadorEDA  # ¡No olvides importar esto!


    def main():
        URL = "https://raw.githubusercontent.com/martj42/international_results/master/results.csv"

        # 1. Ingesta: Asignamos el resultado a la variable 'df'
        cargador = CargadorDatos(URL)
        df = cargador.descargar_y_filtrar()

        # 2. Gestión
        gestor = GestorPartidos(df)
        partidos_cr = gestor.get_por_equipo("Costa Rica")
        print(f"Partidos de Costa Rica encontrados: {len(partidos_cr)}")

        # 3. Procesamiento EDA: Usamos la MISMA variable 'df'
        procesador = ProcesadorEDA(df)
        df_limpio = procesador.limpieza_datos()
        df_final = procesador.crear_columnas_derivadas()

        # 4. Persistencia
        cargador.guardar_procesado(df_final)
        print("Proceso completado exitosamente.")


    if __name__ == "__main__":
        main()