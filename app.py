import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(
    page_title="Dashboard Ejecutivo",
    layout="wide",
    initial_sidebar_state="expanded"  # 👈 sidebar visible
)

st.title("📊 Dashboard Ejecutivo de Asistencia")

# -----------------------
# DATA
# -----------------------
@st.cache_data
def cargar():
    return pd.read_csv("asistencia_detalle.csv")

df = cargar()

# -----------------------
# LIMPIEZA (IMPORTANTE)
# -----------------------
df['score'] = df['tardanzas']*2 + df['retiros_tempranos']
df['id_estudiante'] = df['id_estudiante'].astype(str)

def segmentar(score):
    if score <= 5:
        return "Bueno"
    elif score <= 15:
        return "Regular"
    else:
        return "Crítico"

df['segmento'] = df['score'].apply(segmentar)

# -----------------------
# SIDEBAR
# -----------------------
st.sidebar.title("🎛️ Filtros")

periodos = st.sidebar.multiselect(
    "Periodo",
    sorted(df['id_periodo'].unique()),
    default=sorted(df['id_periodo'].unique())
)

estudiantes = st.sidebar.multiselect(
    "Estudiantes",
    sorted(df['id_estudiante'].unique())
)

rango_tardanzas = st.sidebar.slider(
    "Rango tardanzas",
    int(df['tardanzas'].min()),
    int(df['tardanzas'].max()),
    (int(df['tardanzas'].min()), int(df['tardanzas'].max()))
)

# -----------------------
# FILTRADO
# -----------------------
df_f = df[df['id_periodo'].isin(periodos)]

if estudiantes:
    df_f = df_f[df_f['id_estudiante'].isin(estudiantes)]

df_f = df_f[
    df_f['tardanzas'].between(rango_tardanzas[0], rango_tardanzas[1])
]

# -----------------------
# VALIDACIÓN
# -----------------------
if df_f.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
    st.stop()

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tardanzas Prom", round(df_f['tardanzas'].mean(),2))
col2.metric("Retiros Prom", round(df_f['retiros_tempranos'].mean(),2))
col3.metric("Score Prom", round(df_f['score'].mean(),2))
col4.metric("Casos Críticos", len(df_f[df_f['segmento']=="Crítico"]))

st.divider()

# -----------------------
# HISTOGRAMAS (CLAROS)
# -----------------------
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_f, x="tardanzas", nbins=20,
                       title="Distribución de Tardanzas")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df_f, x="score", nbins=20,
                       title="Distribución del Score")
    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SCATTER
# -----------------------
st.subheader("🔗 Relación")

fig = px.scatter(
    df_f,
    x="tardanzas",
    y="retiros_tempranos",
    color="segmento",
    hover_data=["id_estudiante"]
)
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SEGMENTACIÓN
# -----------------------
st.subheader("📊 Segmentación")

seg = df_f['segmento'].value_counts().reset_index()
seg.columns = ['segmento', 'cantidad']

fig = px.bar(seg, x="segmento", y="cantidad", color="segmento")
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TENDENCIA
# -----------------------
st.subheader("📈 Tendencia")

tend = df.groupby('id_periodo')['score'].mean().reset_index()

fig = px.line(tend, x="id_periodo", y="score", markers=True)
fig.update_layout(template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TOP ESTUDIANTES (FIX TOTAL)
# -----------------------
st.subheader("🏆 Top 10 Estudiantes")

top = df_f.groupby('id_estudiante')['score'] \
    .sum() \
    .sort_values(ascending=False) \
    .head(10) \
    .reset_index()

if not top.empty:
    fig = px.bar(
        top,
        x="score",
        y="id_estudiante",
        orientation="h",
        color="score",
        title="Top Estudiantes",
        color_continuous_scale="Blues"
    )
    fig.update_layout(
        template="plotly_white",
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No hay datos para mostrar en Top estudiantes")

# -----------------------
# INSIGHTS
# -----------------------
st.subheader("🧠 Insights")

if df_f['tardanzas'].mean() > 5:
    st.error("🚨 Alto nivel de tardanzas")
elif df_f['tardanzas'].mean() > 3:
    st.warning("⚠️ Nivel medio")
else:
    st.success("✅ Buen nivel")

# -----------------------
# TABLA
# -----------------------
st.subheader("🔍 Datos")

st.dataframe(df_f, use_container_width=True)

# -----------------------
# DESCARGA
# -----------------------
csv = df_f.to_csv(index=False)

st.download_button("📥 Descargar CSV", csv, "datos.csv")
