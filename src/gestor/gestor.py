<<<<<<< Updated upstream
=======
"""Modulo gestor: consultas de solo lectura sobre el DataFrame de partidos."""

import pandas as pd


class GestorPartidos:
    """
    Expone metodos de SOLO LECTURA para consultar el historico de partidos.

    Ninguno de estos metodos modifica el DataFrame original: en el constructor
    se trabaja sobre una copia y las consultas siempre devuelven vistas nuevas.
    """

    def __init__(self, df):
        # Se copia para que las consultas nunca alteren el DataFrame del llamador.
        self.df = df.copy()

        # La fecha se normaliza una sola vez aqui. Antes esto se hacia dentro de
        # get_por_anio(), lo que convertia una consulta de lectura en una escritura.
        if not pd.api.types.is_datetime64_any_dtype(self.df["date"]):
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")

        # Se garantiza la columna 'year' aunque el EDA todavia no se haya corrido.
        if "year" not in self.df.columns:
            self.df["year"] = self.df["date"].dt.year

    # ------------------------------------------------------------------
    # Consultas basicas
    # ------------------------------------------------------------------
    def get_partido(self, id_partido):
        """Retorna un partido especifico por indice."""
        if id_partido not in self.df.index:
            raise KeyError(f"No existe un partido con el indice {id_partido}.")
        return self.df.loc[id_partido]

    def get_por_equipo(self, equipo):
        """Retorna todos los partidos donde participo un equipo (local o visitante)."""
        return self.df[
            (self.df["home_team"] == equipo) | (self.df["away_team"] == equipo)
        ].copy()

    def get_por_anio(self, anio):
        """Retorna los partidos de una edicion (anio) especifica."""
        return self.df[self.df["year"] == anio].copy()

    def get_por_sede(self, pais):
        """Retorna los partidos jugados en un pais sede."""
        return self.df[self.df["country"] == pais].copy()

    def get_por_ciudad(self, ciudad):
        """Retorna los partidos jugados en una ciudad especifica."""
        return self.df[self.df["city"] == ciudad].copy()

    def get_por_rango_anios(self, anio_inicio, anio_fin):
        """Retorna los partidos jugados entre dos ediciones, ambas incluidas."""
        return self.df[
            (self.df["year"] >= anio_inicio) & (self.df["year"] <= anio_fin)
        ].copy()

    def get_enfrentamientos(self, equipo_a, equipo_b):
        """Retorna el historial de duelos directos entre dos selecciones."""
        return self.df[
            ((self.df["home_team"] == equipo_a) & (self.df["away_team"] == equipo_b))
            | ((self.df["home_team"] == equipo_b) & (self.df["away_team"] == equipo_a))
        ].copy()

    # ------------------------------------------------------------------
    # Catalogos
    # ------------------------------------------------------------------
    def get_equipos(self):
        """Lista ordenada de todas las selecciones que han jugado un Mundial."""
        equipos = pd.concat([self.df["home_team"], self.df["away_team"]])
        return sorted(equipos.unique())

    def get_ediciones(self):
        """Lista ordenada de los anios en que se jugo un Mundial."""
        return sorted(self.df["year"].dropna().unique().tolist())

    def get_sedes(self):
        """Lista ordenada de los paises que han sido sede."""
        return sorted(self.df["country"].dropna().unique())

    # ------------------------------------------------------------------
    # Estadisticas agregadas
    # ------------------------------------------------------------------
    def ventaja_local(self):
        """Estadisticas globales de cuanto pesa jugar como equipo local."""
        total = len(self.df)
        if total == 0:
            return {"total_partidos": 0, "victorias_local": 0, "porcentaje": 0.0}

        locales_ganan = int((self.df["home_score"] > self.df["away_score"]).sum())
        return {
            "total_partidos": total,
            "victorias_local": locales_ganan,
            "porcentaje": (locales_ganan / total) * 100,
        }

    def ventaja_local_por_neutralidad(self):
        """
        Compara el rendimiento del local segun la cancha sea neutral o no.

        En un Mundial casi todos los partidos son en cancha neutral, asi que el
        'local' es solo una etiqueta del calendario. Esta consulta permite aislar
        los partidos donde de verdad habia localia y medir cuanto vale.
        """
        resultado = {}
        for es_neutral, grupo in self.df.groupby("neutral"):
            total = len(grupo)
            ganados = int((grupo["home_score"] > grupo["away_score"]).sum())
            etiqueta = "cancha_neutral" if es_neutral else "localia_real"
            resultado[etiqueta] = {
                "total_partidos": total,
                "victorias_local": ganados,
                "porcentaje": (ganados / total) * 100 if total else 0.0,
            }
        return resultado

    def resumen_equipo(self, equipo):
        """
        Ficha historica de una seleccion: partidos jugados, ganados, empatados,
        perdidos, goles a favor, en contra y diferencia.
        """
        partidos = self.get_por_equipo(equipo)
        if partidos.empty:
            raise ValueError(f"La seleccion '{equipo}' no registra partidos de Mundial.")

        es_local = partidos["home_team"] == equipo

        # Goles a favor y en contra segun el equipo haya sido local o visitante.
        goles_favor = partidos["home_score"].where(es_local, partidos["away_score"])
        goles_contra = partidos["away_score"].where(es_local, partidos["home_score"])

        ganados = int((goles_favor > goles_contra).sum())
        empatados = int((goles_favor == goles_contra).sum())
        perdidos = int((goles_favor < goles_contra).sum())

        return {
            "equipo": equipo,
            "partidos_jugados": len(partidos),
            "ganados": ganados,
            "empatados": empatados,
            "perdidos": perdidos,
            "goles_favor": int(goles_favor.sum()),
            "goles_contra": int(goles_contra.sum()),
            "diferencia_goles": int(goles_favor.sum() - goles_contra.sum()),
            "mundiales_jugados": partidos["year"].nunique(),
        }

    def tabla_historica(self, minimo_partidos=10):
        """
        Construye la tabla historica de todas las selecciones, ordenada por
        diferencia de goles. Responde a '?que seleccion tiene la mejor
        diferencia de goles historica?'.

        Args:
            minimo_partidos: filtra equipos con pocos partidos, que distorsionan
                             el ranking con muestras muy chicas.
        """
        filas = [self.resumen_equipo(equipo) for equipo in self.get_equipos()]
        tabla = pd.DataFrame(filas)
        tabla = tabla[tabla["partidos_jugados"] >= minimo_partidos]
        return tabla.sort_values("diferencia_goles", ascending=False).reset_index(drop=True)

    def goles_por_edicion(self):
        """
        Goles totales y promedio por partido en cada Mundial.
        Responde a '?en que Mundial se metieron mas goles por partido?'.
        """
        base = self.df.copy()
        if "total_goals" not in base.columns:
            base["total_goals"] = base["home_score"] + base["away_score"]

        resumen = base.groupby("year").agg(
            partidos=("total_goals", "count"),
            goles_totales=("total_goals", "sum"),
            goles_por_partido=("total_goals", "mean"),
        )
        return resumen.round(2)

    def partidos_mas_goleados(self, n=10):
        """Los n partidos con mas goles en la historia de los Mundiales."""
        base = self.df.copy()
        if "total_goals" not in base.columns:
            base["total_goals"] = base["home_score"] + base["away_score"]

        columnas = ["date", "home_team", "home_score", "away_score", "away_team", "total_goals"]
        return base.nlargest(n, "total_goals")[columnas].reset_index(drop=True)

    def rendimiento_pais_sede(self):
        """
        Compara como le fue a cada pais cuando jugo de local en su propio Mundial.
        Responde a '?el pais sede gana mas?'.
        """
        filas = []
        for pais in self.get_sedes():
            # Partidos de la sede jugando en casa, con localia real (no neutral).
            en_casa = self.df[
                (self.df["country"] == pais)
                & (~self.df["neutral"].astype(bool))
                & ((self.df["home_team"] == pais) | (self.df["away_team"] == pais))
            ]
            if en_casa.empty:
                continue

            es_local = en_casa["home_team"] == pais
            goles_favor = en_casa["home_score"].where(es_local, en_casa["away_score"])
            goles_contra = en_casa["away_score"].where(es_local, en_casa["home_score"])

            jugados = len(en_casa)
            ganados = int((goles_favor > goles_contra).sum())
            filas.append({
                "sede": pais,
                "partidos_en_casa": jugados,
                "ganados": ganados,
                "porcentaje_victorias": round((ganados / jugados) * 100, 1),
            })

        return pd.DataFrame(filas).sort_values(
            "porcentaje_victorias", ascending=False
        ).reset_index(drop=True)
>>>>>>> Stashed changes
