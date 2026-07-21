# ⚽ World Cup Insights

Sistema de análisis de datos de la Copa Mundial de la FIFA (1930–2026), desarrollado
en Python con Programación Orientada a Objetos.

**Curso:** BD-143 Programación II — II Cuatrimestre 2026
**Colegio Universitario de Cartago — BIG DATA**
**Profesor:** Osvaldo González Chaves

El sistema ingesta los partidos de Copa Mundial desde un CSV público, los procesa en
memoria mediante clases bien definidas, y permite consultas, análisis exploratorio
(EDA) y visualización estática e interactiva.

---

## 📋 Requisitos

- Python 3.11 o superior (probado en 3.13.1)
- Conexión a internet **solo la primera vez**, para descargar el dataset

## 🚀 Instalación

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd world_cup_insights

# 2. Crear y activar un entorno virtual
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

# 3. Instalar las dependencias
pip install -r requirements.txt
```

## ▶️ Ejecución

### Flujo completo (recomendado para empezar)

```bash
python main.py
```

Ejecuta las cuatro etapas del sistema: descarga y filtra los partidos, los limpia y
genera las columnas derivadas, guarda el dataset procesado en `data/processed/` y
demuestra las consultas del gestor.

### Notebooks

```bash
jupyter notebook
```

- **`notebooks/01_EDA.ipynb`** — ingesta, limpieza, estadística descriptiva,
  correlaciones, outliers y consultas. Invoca `CargadorDatos`, `ProcesadorEDA` y
  `GestorPartidos`.
- **`notebooks/02_Visualizacion.ipynb`** — los nueve gráficos con su lectura
  analítica. Invoca `Visualizador`.

### Dashboard interactivo

```bash
streamlit run dashboard/app.py
```

Se abre en `http://localhost:8501` con filtros por edición, selección y tipo de
localía, cuatro pestañas de análisis y descarga de los datos filtrados.

---

## 📁 Estructura del proyecto

```
world_cup_insights/
├── src/                          # Código fuente
│   ├── ingesta/cargador.py       # Clase CargadorDatos
│   ├── gestor/gestor.py          # Clase GestorPartidos
│   ├── eda/procesador.py         # Clase ProcesadorEDA
│   ├── visualizacion/visualizador.py  # Clase Visualizador
│   └── helpers/utilidades.py     # Clase Utilidades
│
├── notebooks/
│   ├── 01_EDA.ipynb
│   └── 02_Visualizacion.ipynb
│
├── data/
│   ├── raw/partidos-mundial.csv              # CSV filtrado desde la fuente
│   └── processed/partidos-mundial-procesado.csv  # Dataset final (CSV y JSON)
│
├── reports/figuras/              # Gráficos generados (PNG + HTML interactivo)
├── dashboard/app.py              # Dashboard de Streamlit
├── main.py                       # Punto de entrada
└── requirements.txt
```

---

## 🧱 Diseño orientado a objetos

| Clase | Módulo | Responsabilidad |
|---|---|---|
| `CargadorDatos` | `src/ingesta/` | Descarga, filtra, valida y persiste (CSV/JSON) |
| `GestorPartidos` | `src/gestor/` | Consultas de **solo lectura** sobre el DataFrame |
| `ProcesadorEDA` | `src/eda/` | Limpieza, columnas derivadas y estadística |
| `Visualizador` | `src/visualizacion/` | Construcción de los gráficos |
| `Utilidades` | `src/helpers/` | Formateo, validaciones y rutas |

Cada clase tiene una única responsabilidad y no conoce los detalles internos de las
demás: se comunican pasándose DataFrames. `GestorPartidos` y `ProcesadorEDA` trabajan
siempre sobre **copias**, de modo que ninguna consulta altera los datos originales.

### Métodos principales

**`CargadorDatos`** — `descargar_y_filtrar_raw()`, `cargar_raw_local()`,
`obtener_datos()`, `validar_columnas()`, `validar_datos()`, `guardar_procesado()`,
`guardar_procesado_json()`, `cargar_procesado()`

**`GestorPartidos`** — `get_partido()`, `get_por_equipo()`, `get_por_anio()`,
`get_por_sede()`, `get_por_ciudad()`, `get_por_rango_anios()`, `get_enfrentamientos()`,
`get_equipos()`, `get_ediciones()`, `get_sedes()`, `ventaja_local()`,
`ventaja_local_por_neutralidad()`, `resumen_equipo()`, `tabla_historica()`,
`goles_por_edicion()`, `partidos_mas_goleados()`, `rendimiento_pais_sede()`

**`ProcesadorEDA`** — `limpieza_datos()`, `crear_columnas_derivadas()`,
`resumen_descriptivo()`, `matriz_correlacion()`, `reporte_nulos()`,
`detectar_outliers()`, `agrupar_por_edicion()`, `agrupar_por_decada()`,
`distribucion_resultados()`

**`Visualizador`** — `histograma_goles()`, `ventaja_local_real()`,
`evolucion_goles_por_edicion()`, `heatmap_correlacion()`, `top_equipos_diferencia()`,
`dispersion_ataque_defensa()`, `rendimiento_sedes()`, `distribucion_resultados()`,
`grafico_interactivo_goles()`, `generar_todos()`

---

## 📊 Dataset

**Fuente:** [International football results from 1872 to 2026](https://github.com/martj42/international_results) (martj42)
**CSV:** `https://raw.githubusercontent.com/martj42/international_results/master/results.csv`

Se filtran los registros con `tournament == "FIFA World Cup"`: **1 068 partidos**
entre 1930 y 2026.

### Columnas derivadas que genera el sistema

| Columna | Descripción |
|---|---|
| `year` | Edición del Mundial |
| `total_goals` | Goles totales del partido |
| `goal_diff` | Diferencia de goles (local − visitante) |
| `winner` | `Local` / `Visitante` / `Empate` |
| `decada` | Década, para agrupaciones |
| `es_empate` | Booleano de apoyo |

---

## 🔍 Principales hallazgos

**1. La ventaja de local es real, pero el promedio global la esconde.**

| Escenario | Gana el local | Partidos |
|---|---|---|
| Localía real (el país sede en su casa) | **61.2 %** | 134 |
| Cancha neutral | 43.5 % | 934 |
| *Promedio global* | *45.7 %* | *1 068* |

El promedio global sugiere que ser local casi no importa. Al separar los grupos
aparece una diferencia de casi 18 puntos. Como el 87 % de los partidos de Mundial se
juegan en cancha neutral, ese grupo mayoritario arrastra la media: es un caso de
**paradoja de Simpson** en datos reales.

**2. El fútbol de Mundial se volvió más cerrado.** Del pico de **5.38 goles por
partido en 1954** al piso de **2.21 en 1990**; desde entonces se estabilizó cerca
de 2.6.

**3. Los países sede rinden mejor en casa:** Uruguay 100 %, Inglaterra 83 %,
Italia 83 %, Alemania 79 %.

**4. Brasil domina el histórico** con **+135** de diferencia de goles, por delante de
Alemania (+108) y Argentina (+62).

**5. El partido más goleado:** Suiza 5–7 Austria (1954), con 12 goles.

> **Nota metodológica.** Los gráficos por edición usan el **promedio de goles por
> partido**, no el total: el torneo pasó de 18 partidos en 1930 a **104 en 2026**
> (formato de 48 equipos), así que los totales no son comparables entre ediciones.

---

## 📈 Gráficos generados

Todos se guardan en `reports/figuras/`:

| Archivo | Pregunta que responde |
|---|---|
| `01_histograma_goles.png` | ¿Cuántos goles se ven en un partido? |
| `02_ventaja_local.png` | ¿Cuánto vale jugar en casa? |
| `03_evolucion_goles.png` | ¿El fútbol se volvió más defensivo? |
| `04_heatmap_correlacion.png` | ¿Cómo se relacionan las variables? |
| `05_top_equipos.png` | ¿Qué selección domina el histórico? |
| `06_ataque_defensa.png` | ¿Se gana atacando o defendiendo? |
| `07_rendimiento_sedes.png` | ¿El país sede gana más? |
| `08_distribucion_resultados.png` | ¿Cómo termina un partido típico? |
| `09_interactivo_goles.html` | Versión interactiva (Plotly) |

---

## 🛠️ Solución de problemas

**`ModuleNotFoundError: No module named 'src'`**
Ejecute los comandos desde la raíz del proyecto (la carpeta que contiene `main.py`).

**`FileNotFoundError` en los notebooks o el dashboard**
Ejecute primero `python main.py` para generar el dataset procesado.

**No hay conexión a internet**
Si `data/raw/partidos-mundial.csv` ya existe, el sistema lo reutiliza y funciona sin
conexión. `obtener_datos()` descarga solo cuando el archivo no está.
