"""
Dashboard interactivo de World Cup Insights.

Ejecutar desde la raiz del proyecto con:
    streamlit run dashboard/app.py
"""

import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st

# La raiz del proyecto se agrega al path para poder importar el paquete src
# cuando Streamlit ejecuta este archivo desde la carpeta dashboard/.
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ not in sys.path:
    sys.path.insert(0, RAIZ)

from src.ingesta.cargador import CargadorDatos
from src.eda.procesador import ProcesadorEDA
from src.gestor.gestor import GestorPartidos

RUTA_PROCESSED = os.path.join(RAIZ, "data", "processed", "partidos-mundial-procesado.csv")
RUTA_RAW = os.path.join(RAIZ, "data", "raw", "partidos-mundial.csv")

st.set_page_config(page_title="World Cup Insights", page_icon="⚽", layout="wide")


# ----------------------------------------------------------------------
# Carga de datos
# ----------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    """
    Carga el dataset procesado. Si todavia no existe, ejecuta el flujo de
    ingesta y EDA para generarlo, de modo que el dashboard funcione aunque
    sea lo primero que se ejecute del proyecto.
    """
    cargador = CargadorDatos(ruta_raw=RUTA_RAW, ruta_processed=RUTA_PROCESSED)

    if os.path.exists(RUTA_PROCESSED):
        return cargador.cargar_procesado()

    df_raw = cargador.obtener_datos()
    procesador = ProcesadorEDA(df_raw)
    procesador.limpieza_datos()
    df = procesador.crear_columnas_derivadas()
    cargador.guardar_procesado(df)
    return df


df = cargar_datos()
gestor = GestorPartidos(df)

# ----------------------------------------------------------------------
# Encabezado
# ----------------------------------------------------------------------
st.title("⚽ World Cup Insights")
st.caption(
    "Analisis de los partidos de la Copa Mundial de la FIFA (1930-2026) | "
    "Proyecto II - BD-143 Programacion II"
)

# ----------------------------------------------------------------------
# Filtros
# ----------------------------------------------------------------------
st.sidebar.header("Filtros")

ediciones = gestor.get_ediciones()
rango = st.sidebar.select_slider(
    "Rango de ediciones",
    options=ediciones,
    value=(ediciones[0], ediciones[-1]),
)

equipos = ["Todas"] + gestor.get_equipos()
equipo_sel = st.sidebar.selectbox("Seleccion", equipos)

solo_localia = st.sidebar.checkbox(
    "Solo partidos con localia real",
    value=False,
    help="Excluye los partidos jugados en cancha neutral.",
)

# Se aplican los filtros usando los metodos de solo lectura del gestor.
df_filtrado = gestor.get_por_rango_anios(rango[0], rango[1])

if equipo_sel != "Todas":
    df_filtrado = df_filtrado[
        (df_filtrado["home_team"] == equipo_sel) | (df_filtrado["away_team"] == equipo_sel)
    ]

if solo_localia:
    df_filtrado = df_filtrado[~df_filtrado["neutral"].astype(bool)]

if df_filtrado.empty:
    st.warning("No hay partidos que cumplan con los filtros seleccionados.")
    st.stop()

# ----------------------------------------------------------------------
# Metricas principales
# ----------------------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Partidos", len(df_filtrado))
col2.metric("Goles totales", int(df_filtrado["total_goals"].sum()))
col3.metric("Goles por partido", f"{df_filtrado['total_goals'].mean():.2f}")
col4.metric(
    "Gana el local",
    f"{(df_filtrado['home_score'] > df_filtrado['away_score']).mean() * 100:.1f}%",
)

st.divider()

# ----------------------------------------------------------------------
# Pestañas
# ----------------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(
    ["Tendencias", "La ventaja de local", "Selecciones", "Datos"]
)

# --- Tendencias -------------------------------------------------------
with tab1:
    st.subheader("Promedio de goles por partido en cada Mundial")

    resumen = df_filtrado.groupby("year").agg(
        promedio_goles=("total_goals", "mean"),
        partidos=("total_goals", "count"),
        goles_totales=("total_goals", "sum"),
    ).reset_index().round(2)

    fig = px.line(
        resumen, x="year", y="promedio_goles", markers=True,
        hover_data=["partidos", "goles_totales"],
        labels={"year": "Edicion", "promedio_goles": "Goles por partido"},
    )
    fig.update_layout(hovermode="x unified", template="plotly_white")
    st.plotly_chart(fig, width='stretch')

    st.info(
        "Se grafica el **promedio** y no el total de goles: el torneo paso de 18 "
        "partidos en 1930 a 104 en 2026, asi que los totales no son comparables "
        "entre ediciones."
    )

    st.subheader("Distribucion de goles por partido")
    fig_hist = px.histogram(
        df_filtrado, x="total_goals", nbins=13,
        labels={"total_goals": "Goles en el partido", "count": "Partidos"},
    )
    fig_hist.update_layout(template="plotly_white", bargap=0.08)
    st.plotly_chart(fig_hist, width='stretch')

# --- Ventaja de local -------------------------------------------------
with tab2:
    st.subheader("La ventaja de local es real, pero el promedio la esconde")

    neutral = df_filtrado["neutral"].astype(bool)
    grupos = {
        "Localia real": df_filtrado[~neutral],
        "Cancha neutral": df_filtrado[neutral],
    }

    filas = []
    for etiqueta, grupo in grupos.items():
        if grupo.empty:
            continue
        filas.append({
            "Escenario": etiqueta,
            "Victorias del local (%)": round(
                (grupo["home_score"] > grupo["away_score"]).mean() * 100, 1
            ),
            "Partidos": len(grupo),
        })

    if len(filas) < 2:
        st.warning(
            "Con los filtros actuales solo hay un escenario disponible. "
            "Desactive 'Solo partidos con localia real' para ver la comparacion."
        )
    else:
        comparacion = pd.DataFrame(filas)
        global_pct = (
            df_filtrado["home_score"] > df_filtrado["away_score"]
        ).mean() * 100

        fig_v = px.bar(
            comparacion, x="Escenario", y="Victorias del local (%)",
            color="Escenario", text="Victorias del local (%)",
            hover_data=["Partidos"],
            color_discrete_map={"Localia real": "#2a9d8f", "Cancha neutral": "#adb5bd"},
        )
        fig_v.add_hline(
            y=global_pct, line_dash="dash", line_color="crimson",
            annotation_text=f"Promedio global: {global_pct:.1f}%",
        )
        fig_v.update_traces(textposition="inside", texttemplate="%{text}%")
        fig_v.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig_v, width='stretch')

        st.success(
            "**Paradoja de Simpson.** El promedio global sugiere que ser local casi "
            "no importa, pero al separar los grupos la localia real gana muy por "
            "encima. Como la mayoria de los partidos de Mundial son en cancha "
            "neutral, ese grupo arrastra la media hacia abajo."
        )

    st.subheader("Rendimiento del pais sede jugando en casa")
    st.dataframe(gestor.rendimiento_pais_sede(), width='stretch', hide_index=True)

# --- Selecciones ------------------------------------------------------
with tab3:
    st.subheader("Tabla historica por diferencia de goles")

    minimo = st.slider("Minimo de partidos jugados", 1, 50, 10)
    tabla = gestor.tabla_historica(minimo_partidos=minimo)
    st.dataframe(tabla, width='stretch', hide_index=True)

    fig_top = px.bar(
        tabla.head(15).sort_values("diferencia_goles"),
        x="diferencia_goles", y="equipo", orientation="h",
        color="diferencia_goles", color_continuous_scale="Viridis",
        labels={"diferencia_goles": "Diferencia de goles", "equipo": ""},
    )
    fig_top.update_layout(template="plotly_white", height=520)
    st.plotly_chart(fig_top, width='stretch')

    if equipo_sel != "Todas":
        st.subheader(f"Ficha historica: {equipo_sel}")
        st.json(gestor.resumen_equipo(equipo_sel))

# --- Datos ------------------------------------------------------------
with tab4:
    st.subheader("Partidos con mas goles")
    st.dataframe(
        gestor.partidos_mas_goleados(15), width='stretch', hide_index=True
    )

    st.subheader("Datos filtrados")
    st.dataframe(df_filtrado, width='stretch', hide_index=True)

    st.download_button(
        "Descargar seleccion en CSV",
        data=df_filtrado.to_csv(index=False).encode("utf-8"),
        file_name="partidos-mundial-filtrado.csv",
        mime="text/csv",
    )
