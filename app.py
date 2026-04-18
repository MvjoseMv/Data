import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# -----------------------
# ESTILO GLOBAL
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
# CARGA DE DATOS
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
# SIDEBAR FILTROS
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
    "Rango de tardanzas",
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
# KPIs
# -----------------------
st.subheader("📌 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tardanzas Promedio", round(df_f['tardanzas'].mean(),2))
col2.metric("Retiros Promedio", round(df_f['retiros_tempranos'].mean(),2))
col3.metric("Score Promedio", round(df_f['score'].mean(),2))
col4.metric("Casos Críticos", len(df_f[df_f['segmento']=="Crítico"]))

st.divider()

# -----------------------
# HISTOGRAMAS PRO
# -----------------------
col1, col2 = st.columns(2)

with col1:
    fig = px.histogram(
        df_f,
        x="tardanzas",
        nbins=20,
        title="Distribución de Tardanzas",
        opacity=0.85
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        title_font=dict(size=20),
        bargap=0.05
    )
    fig.update_traces(
        marker_color="#00c2ff",
        marker_line_width=1,
        marker_line_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        df_f,
        x="score",
        nbins=20,
        title="Distribución del Score",
        opacity=0.85
    )
    fig.update_layout(
        template="plotly_dark",
        plot_bgcolor="#1e1e1e",
        paper_bgcolor="#0e1117",
        font=dict(color="white"),
        title_font=dict(size=20),
        bargap=0.05
    )
    fig.update_traces(
        marker_color="#ff7f0e",
        marker_line_width=1,
        marker_line_color="white"
    )
    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SCATTER INTERACTIVO
# -----------------------
st.subheader("🔗 Relación entre Tardanzas y Retiros")

fig = px.scatter(
    df_f,
    x="tardanzas",
    y="retiros_tempranos",
    color="segmento",
    hover_data=["id_estudiante"],
    title="Relación entre variables"
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#0e1117",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SEGMENTACIÓN CORRECTA
# -----------------------
st.subheader("📊 Segmentación de Estudiantes")

segmento_df = df_f['segmento'].value_counts().reset_index()
segmento_df.columns = ['segmento', 'cantidad']

fig = px.bar(
    segmento_df,
    x="segmento",
    y="cantidad",
    color="segmento",
    title="Distribución de Segmentos"
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#0e1117",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TENDENCIA
# -----------------------
st.subheader("📈 Tendencia por Periodo")

tendencia = df.groupby('id_periodo')['score'].mean().reset_index()

fig = px.line(
    tendencia,
    x="id_periodo",
    y="score",
    markers=True,
    title="Evolución del Score"
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#0e1117",
    font=dict(color="white")
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# TOP ESTUDIANTES (ARREGLADO)
# -----------------------
st.subheader("🏆 Top 10 Estudiantes")

top = df_f.groupby('id_estudiante')['score'] \
    .sum() \
    .sort_values(ascending=False) \
    .head(10) \
    .reset_index()

fig = px.bar(
    top,
    x="score",
    y="id_estudiante",
    orientation="h",
    title="Top 10 Estudiantes con Mayor Score",
    color="score",
    color_continuous_scale="Blues"
)

fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#0e1117",
    font=dict(color="white"),
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# INSIGHTS AUTOMÁTICOS
# -----------------------
st.subheader("🧠 Insights")

if df_f['tardanzas'].mean() > 5:
    st.error("🚨 Alto nivel de tardanzas detectado")
elif df_f['tardanzas'].mean() > 3:
    st.warning("⚠️ Nivel medio de tardanzas")
else:
    st.success("✅ Buen nivel de asistencia")

# -----------------------
# TABLA INTERACTIVA
# -----------------------
st.subheader("🔍 Exploración de datos")

st.dataframe(df_f, use_container_width=True)

# -----------------------
# EXPORTAR
# -----------------------
st.subheader("📥 Descargar datos")

csv = df_f.to_csv(index=False)

st.download_button(
    "Descargar CSV",
    csv,
    "datos_filtrados.csv"
)
