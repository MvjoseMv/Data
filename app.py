import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------
# CONFIG
# -----------------------
st.set_page_config(
    page_title="Dashboard Ejecutivo",
    layout="wide",
    initial_sidebar_state="expanded"
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
# LIMPIEZA Y FEATURES
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
# VALIDACIÓN
# -----------------------
if df_f.empty:
    st.warning("⚠️ No hay datos con los filtros seleccionados")
    st.stop()

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tardanzas Prom", round(df_f['tardanzas'].mean(),2))
col2.metric("Retiros Prom", round(df_f['retiros_tempranos'].mean(),2))
col3.metric("Score Prom", round(df_f['score'].mean(),2))
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
        nbins=25,
        marginal="box",
        opacity=0.9,
        color_discrete_sequence=["#4CAF50"]
    )

    fig.add_vline(
        x=df_f["tardanzas"].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text="Promedio"
    )

    fig.update_layout(
        template="plotly_white",
        title="Distribución de Tardanzas",
        xaxis_title="Tardanzas",
        yaxis_title="Frecuencia"
    )

    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.histogram(
        df_f,
        x="score",
        nbins=25,
        marginal="box",
        opacity=0.9,
        color_discrete_sequence=["#2196F3"]
    )

    fig.add_vline(
        x=df_f["score"].mean(),
        line_dash="dash",
        line_color="red",
        annotation_text="Promedio"
    )

    fig.update_layout(
        template="plotly_white",
        title="Distribución del Score",
        xaxis_title="Score",
        yaxis_title="Frecuencia"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------
# SCATTER
# -----------------------
st.subheader("🔗 Relación entre Variables")

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
# TOP ESTUDIANTES
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
    color="score",
    color_continuous_scale="Blues"
)

fig.update_layout(
    template="plotly_white",
    yaxis=dict(autorange="reversed")
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------
# INSIGHTS
# -----------------------
st.subheader("🧠 Insights")

if df_f['tardanzas'].mean() > 5:
    st.error("🚨 Alto nivel de tardanzas detectado")
elif df_f['tardanzas'].mean() > 3:
    st.warning("⚠️ Nivel medio de tardanzas")
else:
    st.success("✅ Buen nivel de asistencia")

# -----------------------
# TABLA
# -----------------------
st.subheader("🔍 Exploración de datos")

st.dataframe(df_f, use_container_width=True)

# -----------------------
# DESCARGA
# -----------------------
csv = df_f.to_csv(index=False)

st.download_button("📥 Descargar CSV", csv, "datos_filtrados.csv")
