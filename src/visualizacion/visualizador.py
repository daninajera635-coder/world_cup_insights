"""Modulo de visualizacion: graficos estaticos e interactivos."""

import os

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from src.helpers.utilidades import Utilidades


class Visualizador:
    """
    Construye los graficos del proyecto.

    Cada metodo responde a una pregunta concreta sobre los datos y devuelve la
    figura de Matplotlib, de modo que pueda mostrarse en un notebook o
    guardarse como PNG en reports/figuras/.
    """

    PALETA = "viridis"
    TAMANIO = (11, 6)

    def __init__(self, df, ruta_figuras=None, guardar=True):
        """
        Args:
            df: DataFrame procesado (con year, total_goals, goal_diff, winner).
            ruta_figuras: carpeta destino de los PNG.
            guardar: si es False, los graficos solo se muestran.
        """
        self.df = df.copy()
        self.guardar = guardar
        self.ruta_figuras = ruta_figuras or Utilidades.ruta_proyecto("reports", "figuras")

        if self.guardar:
            Utilidades.asegurar_carpeta(self.ruta_figuras)

        sns.set_theme(style="whitegrid", palette=self.PALETA)

    # ------------------------------------------------------------------
    # Auxiliar interno
    # ------------------------------------------------------------------
    def _finalizar(self, fig, nombre_archivo):
        """Ajusta el layout y guarda la figura si corresponde."""
        fig.tight_layout()
        if self.guardar:
            ruta = os.path.join(self.ruta_figuras, nombre_archivo)
            fig.savefig(ruta, dpi=150, bbox_inches="tight")
            print(f"[OK] Grafico guardado: {ruta}")
        return fig

    # ------------------------------------------------------------------
    # 1. Distribucion de goles
    # ------------------------------------------------------------------
    def histograma_goles(self):
        """
        HISTORIA: cuantos goles se ven en un partido de Mundial?

        La distribucion esta sesgada a la derecha: lo normal es un partido de
        2 o 3 goles, y las goleadas son excepciones cada vez mas raras.
        """
        fig, ax = plt.subplots(figsize=self.TAMANIO)

        sns.histplot(data=self.df, x="total_goals", bins=range(0, 14),
                     discrete=True, ax=ax, color="#2a6f97", edgecolor="white")

        promedio = self.df["total_goals"].mean()
        ax.axvline(promedio, color="crimson", linestyle="--", linewidth=2,
                   label=f"Promedio: {promedio:.2f} goles")

        ax.set_title("Distribucion de goles por partido en Mundiales (1930-2026)",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Goles totales en el partido")
        ax.set_ylabel("Cantidad de partidos")
        ax.legend()

        return self._finalizar(fig, "01_histograma_goles.png")

    # ------------------------------------------------------------------
    # 2. La ventaja de local
    # ------------------------------------------------------------------
    def ventaja_local_real(self):
        """
        HISTORIA: la 'ventaja de local' del Mundial es un espejismo del promedio.

        Globalmente el local gana ~46% de los partidos, un numero poco
        impresionante. Pero al separar los partidos en cancha neutral de los
        que tienen localia real, aparece la verdad: cuando de verdad se juega
        en casa el local gana ~61%. Como el 87% de los partidos son neutrales,
        el promedio global esconde el efecto.
        """
        neutral = self.df["neutral"].astype(bool)

        grupos = {
            "Localia real\n(pais sede en casa)": self.df[~neutral],
            "Cancha neutral\n(local solo por calendario)": self.df[neutral],
        }

        etiquetas, porcentajes, totales = [], [], []
        for etiqueta, grupo in grupos.items():
            etiquetas.append(etiqueta)
            porcentajes.append((grupo["home_score"] > grupo["away_score"]).mean() * 100)
            totales.append(len(grupo))

        global_pct = (self.df["home_score"] > self.df["away_score"]).mean() * 100

        fig, ax = plt.subplots(figsize=self.TAMANIO)
        barras = ax.bar(etiquetas, porcentajes, color=["#2a9d8f", "#adb5bd"], width=0.55)

        ax.axhline(global_pct, color="crimson", linestyle="--", linewidth=2,
                   label=f"Promedio global engañoso: {global_pct:.1f}%")

        # Las etiquetas van DENTRO de la barra: puestas encima chocaban con la
        # linea del promedio global, que cae justo entre los dos valores.
        for barra, pct, total in zip(barras, porcentajes, totales):
            ax.text(barra.get_x() + barra.get_width() / 2, pct - 3.5,
                    f"{pct:.1f}%\n({total} partidos)",
                    ha="center", va="top", fontweight="bold",
                    color="white", fontsize=12)

        ax.set_title("Jugar en casa si importa: el promedio global lo esconde",
                     fontsize=14, fontweight="bold")
        ax.set_ylabel("Partidos ganados por el equipo local (%)")
        ax.set_ylim(0, 75)
        ax.legend(loc="upper right")

        return self._finalizar(fig, "02_ventaja_local.png")

    # ------------------------------------------------------------------
    # 3. Evolucion de los goles
    # ------------------------------------------------------------------
    def evolucion_goles_por_edicion(self):
        """
        HISTORIA: el futbol de Mundial se volvio mas cerrado con los anios.

        Se grafica el PROMEDIO de goles por partido, no el total: el total no
        es comparable entre ediciones porque el torneo paso de 18 partidos en
        1930 a 104 en 2026. Con el promedio se ve el pico de los anios 50 y la
        caida hacia el futbol tactico moderno.
        """
        resumen = self.df.groupby("year")["total_goals"].agg(["mean", "count"])

        fig, ax = plt.subplots(figsize=self.TAMANIO)
        ax.plot(resumen.index, resumen["mean"], marker="o", linewidth=2.2,
                color="#2a6f97", markersize=7)

        promedio_global = self.df["total_goals"].mean()
        ax.axhline(promedio_global, color="grey", linestyle=":", linewidth=1.5,
                   label=f"Promedio historico: {promedio_global:.2f}")

        # Se anotan el maximo y el minimo historico. Las posiciones se calculan
        # hacia adentro del grafico para que el texto no se salga del area ni
        # choque con el titulo o con la etiqueta del eje X.
        anio_max = resumen["mean"].idxmax()
        anio_min = resumen["mean"].idxmin()
        valor_max = resumen["mean"].max()
        valor_min = resumen["mean"].min()

        # Se agrega aire arriba y abajo para alojar las anotaciones.
        ax.set_ylim(valor_min - 0.55, valor_max + 0.45)

        ax.annotate(f"Maximo: {anio_max}\n{valor_max:.2f} goles/partido",
                    xy=(anio_max, valor_max),
                    xytext=(anio_max + 12, valor_max - 0.12),
                    arrowprops=dict(arrowstyle="->", color="crimson"),
                    fontsize=9, color="crimson", fontweight="bold",
                    va="top")

        ax.annotate(f"Minimo: {anio_min}\n{valor_min:.2f} goles/partido",
                    xy=(anio_min, valor_min),
                    xytext=(anio_min - 30, valor_min + 0.28),
                    arrowprops=dict(arrowstyle="->", color="darkgreen"),
                    fontsize=9, color="darkgreen", fontweight="bold",
                    va="bottom")

        ax.set_title("Promedio de goles por partido en cada Mundial",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Edicion del Mundial")
        ax.set_ylabel("Goles por partido")
        ax.legend(loc="upper right")

        return self._finalizar(fig, "03_evolucion_goles.png")

    # ------------------------------------------------------------------
    # 4. Correlaciones
    # ------------------------------------------------------------------
    def heatmap_correlacion(self):
        """
        HISTORIA: como se relacionan las variables numericas entre si.

        La correlacion negativa entre home_score y away_score muestra que los
        partidos suelen ser desequilibrados: cuando un equipo golea, el otro
        rara vez responde.
        """
        columnas = ["home_score", "away_score", "total_goals", "goal_diff"]
        matriz = self.df[columnas].corr()

        fig, ax = plt.subplots(figsize=(8, 6.5))
        sns.heatmap(matriz, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                    square=True, linewidths=0.5, ax=ax, cbar_kws={"shrink": 0.8})

        ax.set_title("Matriz de correlacion entre variables de marcador",
                     fontsize=13, fontweight="bold", pad=15)

        return self._finalizar(fig, "04_heatmap_correlacion.png")

    # ------------------------------------------------------------------
    # 5. Las mejores selecciones
    # ------------------------------------------------------------------
    def top_equipos_diferencia(self, tabla_historica, n=12):
        """
        HISTORIA: que seleccion domina el historico de Mundiales?

        Args:
            tabla_historica: DataFrame que devuelve GestorPartidos.tabla_historica()
            n: cuantas selecciones mostrar.
        """
        top = tabla_historica.head(n).sort_values("diferencia_goles")

        fig, ax = plt.subplots(figsize=self.TAMANIO)
        colores = sns.color_palette("viridis", len(top))
        ax.barh(top["equipo"], top["diferencia_goles"], color=colores)

        for y, (dif, gf, gc) in enumerate(zip(top["diferencia_goles"],
                                              top["goles_favor"],
                                              top["goles_contra"])):
            ax.text(dif + 1.5, y, f"+{dif}  ({gf}:{gc})", va="center", fontsize=9)

        ax.set_title(f"Top {n} selecciones por diferencia de goles historica",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Diferencia de goles (goles a favor - goles en contra)")
        ax.set_xlim(0, top["diferencia_goles"].max() * 1.22)

        return self._finalizar(fig, "05_top_equipos.png")

    # ------------------------------------------------------------------
    # 6. Ataque contra defensa
    # ------------------------------------------------------------------
    def dispersion_ataque_defensa(self, tabla_historica, n=25):
        """
        HISTORIA: quien gana por atacar y quien por defender?

        Scatter de goles a favor contra goles en contra. Los equipos bajo la
        diagonal tienen saldo positivo; mientras mas abajo y a la derecha, mas
        dominante fue la seleccion.
        """
        top = tabla_historica.head(n)

        fig, ax = plt.subplots(figsize=(11, 7.5))
        dispersion = ax.scatter(top["goles_favor"], top["goles_contra"],
                                s=top["partidos_jugados"] * 3.2,
                                c=top["diferencia_goles"], cmap="RdYlGn",
                                edgecolors="black", linewidth=0.6, alpha=0.85)

        for _, fila in top.iterrows():
            ax.annotate(fila["equipo"],
                        (fila["goles_favor"], fila["goles_contra"]),
                        xytext=(5, 4), textcoords="offset points", fontsize=8)

        # Diagonal de equilibrio: por encima, saldo negativo.
        maximo = max(top["goles_favor"].max(), top["goles_contra"].max()) + 15
        ax.plot([0, maximo], [0, maximo], "--", color="grey", linewidth=1.2,
                label="Equilibrio (goles a favor = en contra)")

        ax.set_title("Ataque contra defensa: el tamaño indica partidos jugados",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Goles a favor")
        ax.set_ylabel("Goles en contra")
        ax.legend(loc="upper left")
        fig.colorbar(dispersion, ax=ax, label="Diferencia de goles")

        return self._finalizar(fig, "06_ataque_defensa.png")

    # ------------------------------------------------------------------
    # 7. El pais sede
    # ------------------------------------------------------------------
    def rendimiento_sedes(self, tabla_sedes, minimo_partidos=4):
        """
        HISTORIA: el pais sede gana mas?

        Args:
            tabla_sedes: DataFrame de GestorPartidos.rendimiento_pais_sede()
            minimo_partidos: descarta sedes con muy pocos partidos en casa.
        """
        datos = tabla_sedes[tabla_sedes["partidos_en_casa"] >= minimo_partidos].copy()
        datos = datos.sort_values("porcentaje_victorias")

        fig, ax = plt.subplots(figsize=self.TAMANIO)
        colores = ["#2a9d8f" if p >= 50 else "#e76f51"
                   for p in datos["porcentaje_victorias"]]
        ax.barh(datos["sede"], datos["porcentaje_victorias"], color=colores)

        ax.axvline(50, color="black", linestyle="--", linewidth=1.3,
                   label="50% (mitad de los partidos ganados)")

        for y, (pct, jugados) in enumerate(zip(datos["porcentaje_victorias"],
                                               datos["partidos_en_casa"])):
            ax.text(pct + 1, y, f"{pct:.0f}% de {jugados}", va="center", fontsize=9)

        ax.set_title("Rendimiento del pais sede jugando en casa",
                     fontsize=14, fontweight="bold")
        ax.set_xlabel("Partidos ganados en casa (%)")
        ax.set_xlim(0, 118)
        ax.legend(loc="lower right")

        return self._finalizar(fig, "07_rendimiento_sedes.png")

    # ------------------------------------------------------------------
    # 8. Reparto de resultados
    # ------------------------------------------------------------------
    def distribucion_resultados(self):
        """
        HISTORIA: como termina un partido de Mundial?

        Se compara el reparto Local / Visitante / Empate y se muestra la
        evolucion del porcentaje de empates por decada, que revela si el
        torneo se volvio mas parejo con el tiempo.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        # Panel izquierdo: reparto global.
        conteo = self.df["winner"].value_counts()
        colores = {"Local": "#2a9d8f", "Visitante": "#e76f51", "Empate": "#adb5bd"}
        ax1.pie(conteo, labels=conteo.index, autopct="%1.1f%%", startangle=90,
                colors=[colores[i] for i in conteo.index],
                wedgeprops={"edgecolor": "white", "linewidth": 2})
        ax1.set_title("Reparto global de resultados", fontsize=12, fontweight="bold")

        # Panel derecho: empates por decada.
        por_decada = self.df.groupby("decada")["es_empate"].mean() * 100
        ax2.plot(por_decada.index, por_decada.values, marker="o",
                 color="#6a4c93", linewidth=2.2)
        ax2.set_title("Porcentaje de empates por decada", fontsize=12, fontweight="bold")
        ax2.set_xlabel("Decada")
        ax2.set_ylabel("Empates (%)")
        ax2.grid(True, alpha=0.35)

        fig.suptitle("Como termina un partido de Mundial", fontsize=14, fontweight="bold")

        return self._finalizar(fig, "08_distribucion_resultados.png")

    # ------------------------------------------------------------------
    # 9. Grafico interactivo (Plotly)
    # ------------------------------------------------------------------
    def grafico_interactivo_goles(self):
        """
        HISTORIA: version interactiva de la evolucion de goles.

        Devuelve una figura de Plotly: al pasar el mouse muestra la cantidad
        de partidos y el promedio exacto de cada edicion.
        """
        import plotly.express as px

        resumen = self.df.groupby("year").agg(
            promedio_goles=("total_goals", "mean"),
            partidos=("total_goals", "count"),
            goles_totales=("total_goals", "sum"),
        ).reset_index().round(2)

        fig = px.line(
            resumen, x="year", y="promedio_goles", markers=True,
            hover_data=["partidos", "goles_totales"],
            title="Promedio de goles por partido en cada Mundial (interactivo)",
            labels={"year": "Edicion", "promedio_goles": "Goles por partido",
                    "partidos": "Partidos jugados", "goles_totales": "Goles totales"},
        )
        fig.update_traces(line=dict(width=3), marker=dict(size=9))
        fig.update_layout(hovermode="x unified", template="plotly_white")

        if self.guardar:
            ruta = os.path.join(self.ruta_figuras, "09_interactivo_goles.html")
            fig.write_html(ruta)
            print(f"[OK] Grafico interactivo guardado: {ruta}")

        return fig

    # ------------------------------------------------------------------
    # Generar todo de una vez
    # ------------------------------------------------------------------
    def generar_todos(self, tabla_historica, tabla_sedes):
        """Genera la bateria completa de graficos estaticos."""
        self.histograma_goles()
        self.ventaja_local_real()
        self.evolucion_goles_por_edicion()
        self.heatmap_correlacion()
        self.top_equipos_diferencia(tabla_historica)
        self.dispersion_ataque_defensa(tabla_historica)
        self.rendimiento_sedes(tabla_sedes)
        self.distribucion_resultados()
        print(f"\n[OK] Todos los graficos estan en: {self.ruta_figuras}")
