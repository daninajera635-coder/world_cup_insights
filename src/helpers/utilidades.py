"""Funciones auxiliares reutilizables por el resto de los modulos."""

import os

import pandas as pd


class Utilidades:
    """
    Agrupa utilidades de formateo, validacion y manejo de archivos.

    Todos los metodos son estaticos: la clase funciona como un espacio de
    nombres, no necesita mantener estado.
    """

    # ------------------------------------------------------------------
    # Archivos y carpetas
    # ------------------------------------------------------------------
    @staticmethod
    def asegurar_carpeta(ruta):
        """Crea la carpeta indicada si todavia no existe y devuelve su ruta."""
        if ruta:
            os.makedirs(ruta, exist_ok=True)
        return ruta

    @staticmethod
    def ruta_proyecto(*partes):
        """
        Arma una ruta absoluta a partir de la raiz del proyecto.

        Evita que el codigo dependa del directorio desde el que se ejecuta,
        que es la causa tipica de que un proyecto 'no corra en otra maquina'.
        """
        raiz = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(raiz, *partes)

    # ------------------------------------------------------------------
    # Formateo
    # ------------------------------------------------------------------
    @staticmethod
    def formatear_marcador(fila):
        """Convierte una fila de partido en un texto legible."""
        return (
            f"{fila['home_team']} {int(fila['home_score'])}-"
            f"{int(fila['away_score'])} {fila['away_team']}"
        )

    @staticmethod
    def formatear_porcentaje(valor, decimales=1):
        """Formatea un numero como porcentaje."""
        return f"{valor:.{decimales}f}%"

    @staticmethod
    def formatear_fecha(fecha):
        """Devuelve la fecha en formato dd/mm/aaaa."""
        return pd.to_datetime(fecha).strftime("%d/%m/%Y")

    # ------------------------------------------------------------------
    # Validaciones
    # ------------------------------------------------------------------
    @staticmethod
    def validar_equipo(df, equipo):
        """
        Comprueba que la seleccion exista en el dataset.

        Si no existe, sugiere nombres parecidos: el dataset usa nombres en
        ingles ('Germany', no 'Alemania') y ese es un error facil de cometer.
        """
        equipos = set(df["home_team"]) | set(df["away_team"])
        if equipo in equipos:
            return True

        parecidos = [e for e in sorted(equipos) if equipo.lower() in e.lower()]
        mensaje = f"La seleccion '{equipo}' no existe en el dataset."
        if parecidos:
            mensaje += f" Quiso decir: {', '.join(parecidos[:5])}?"
        raise ValueError(mensaje)

    @staticmethod
    def validar_anio(df, anio):
        """Comprueba que el anio corresponda a una edicion de Mundial."""
        ediciones = sorted(df["year"].dropna().unique().tolist())
        if anio not in ediciones:
            raise ValueError(
                f"{anio} no es una edicion de Mundial. "
                f"Ediciones disponibles: {ediciones}"
            )
        return True

    # ------------------------------------------------------------------
    # Apoyo al analisis
    # ------------------------------------------------------------------
    @staticmethod
    def goles_del_equipo(partidos, equipo):
        """
        Separa los goles a favor y en contra de un equipo, sin importar si
        jugo de local o de visitante.

        Devuelve una tupla (goles_favor, goles_contra) como Series de pandas.
        """
        es_local = partidos["home_team"] == equipo
        favor = partidos["home_score"].where(es_local, partidos["away_score"])
        contra = partidos["away_score"].where(es_local, partidos["home_score"])
        return favor, contra

    @staticmethod
    def resumen_en_texto(diccionario, titulo=None):
        """Convierte un diccionario de estadisticas en un texto alineado."""
        lineas = []
        if titulo:
            lineas.append(titulo)
            lineas.append("-" * len(titulo))

        ancho = max(len(str(k)) for k in diccionario) if diccionario else 0
        for clave, valor in diccionario.items():
            if isinstance(valor, float):
                valor = f"{valor:.2f}"
            lineas.append(f"{str(clave).ljust(ancho)} : {valor}")
        return "\n".join(lineas)
