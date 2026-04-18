import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# -----------------------
# ESTILO
# -----------------------
st.markdown("""
<style>
.main {
    background-color: #0e1117;
}
h1, h2, h3 {
    color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Ejecutivo de Asistencia")

# -----------------------
# DATA
# -----------------------
@st.cache_data
def cargar():
    return pd.read_csv("asistencia_detalle.csv")

df = cargar()

# -----------------------
# FEATURE ENGINEERING
# -----------------------
df['score'] = df['tardanzas']*2 + df['retiros_tempranos']

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
    df['id_periodo'].unique(),
    default=df['id_periodo'].unique()
)

estudiantes = st.sidebar.multiselect(
    "Estudiantes",
    df['id_estudiante'].unique()
)

# -----------------------
# FILTRO
# -----------------------
df_f = df[df['id_periodo'].isin(periodos)]

if estudiantes:
    df_f = df_f[df_f['id_estudiante'].isin(estudiantes)]

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tardanzas Promedio", round(df_f['tardanzas'].mean(),2))
col2.metric("Retiros Promedio", round(df_f['retiros_tempranos'].mean(),2))
col3.metric("Score Promedio", round(df_f['score'].mean(),2))
col4.metric("Casos Críticos", len(df_f[df_f['segmento']=="Crítico"]))

# -----------------------
# GRÁFICOS INTERACTIVOS
# -----------------------
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(df_f, x="tardanzas", title="Distribución de Tardanzas")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(df_f, x="score", title="Distribución del Score")
    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SCATTER INTERACTIVO
# -----------------------
st.subheader("🔗 Relación entre variables")

fig = px.scatter(
    df_f,
    x="tardanzas",
    y="retiros_tempranos",
    color="segmento",
    hover_data=["id_estudiante"],
    title="Tardanzas vs Retiros"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SEGMENTACIÓN
# -----------------------
st.subheader("📊 Segmentación")

fig = px.bar(
    df_f['segmento'].value_counts().reset_index(),
    x="index",
    y="segmento",
    title="Distribución de Segmentos"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TENDENCIA
# -----------------------
st.subheader("📈 Tendencia")

tendencia = df.groupby('id_periodo')['score'].mean().reset_index()

fig = px.line(tendencia, x="id_periodo", y="score", markers=True)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TOP
# -----------------------
st.subheader("🏆 Top estudiantes")

top = df_f.groupby('id_estudiante')['score'].sum().sort_values(ascending=False).head(10)

fig = px.bar(
    top.reset_index(),
    x="id_estudiante",
    y="score",
    title="Top 10 Estudiantes"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# INSIGHTS
# -----------------------
st.subheader("🧠 Insights")

if df_f['tardanzas'].mean() > 5:
    st.error("🚨 Alto nivel de tardanzas")
elif df_f['tardanzas'].mean() > 3:
    st.warning("⚠️ Nivel medio")
else:
    st.success("✅ Buen nivel de asistencia")

# -----------------------
# TABLA
# -----------------------
st.subheader("🔍 Explorar datos")

st.dataframe(df_f, use_container_width=True)
