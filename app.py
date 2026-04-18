import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard Interactivo", layout="wide")

st.title("📊 Dashboard Interactivo de Asistencia")

# -----------------------
# CARGA
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
st.sidebar.header("🎛️ Filtros Interactivos")

periodos = st.sidebar.multiselect(
    "Periodo",
    sorted(df['id_periodo'].unique()),
    default=sorted(df['id_periodo'].unique())
)

estudiantes = st.sidebar.multiselect(
    "Estudiantes",
    sorted(df['id_estudiante'].unique()),
    default=[]
)

rango_tardanzas = st.sidebar.slider(
    "Rango tardanzas",
    int(df['tardanzas'].min()),
    int(df['tardanzas'].max()),
    (0, int(df['tardanzas'].max()))
)

# -----------------------
# FILTRADO DINÁMICO
# -----------------------
df_filtrado = df[df['id_periodo'].isin(periodos)]

if estudiantes:
    df_filtrado = df_filtrado[df_filtrado['id_estudiante'].isin(estudiantes)]

df_filtrado = df_filtrado[
    df_filtrado['tardanzas'].between(rango_tardanzas[0], rango_tardanzas[1])
]

# -----------------------
# KPIs DINÁMICOS
# -----------------------
st.subheader("📌 Indicadores en Tiempo Real")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Tardanzas Promedio", round(df_filtrado['tardanzas'].mean(),2))
col2.metric("Retiros Promedio", round(df_filtrado['retiros_tempranos'].mean(),2))
col3.metric("Score Promedio", round(df_filtrado['score'].mean(),2))
col4.metric("Casos Críticos", len(df_filtrado[df_filtrado['segmento']=="Crítico"]))

st.divider()

# -----------------------
# GRÁFICOS DINÁMICOS
# -----------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución de Tardanzas")
    fig, ax = plt.subplots()
    df_filtrado['tardanzas'].hist(ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Distribución de Score")
    fig, ax = plt.subplots()
    df_filtrado['score'].hist(ax=ax)
    st.pyplot(fig)

# -----------------------
# RELACIÓN INTERACTIVA
# -----------------------
st.subheader("🔗 Relación entre variables")

fig, ax = plt.subplots()
ax.scatter(df_filtrado['tardanzas'], df_filtrado['retiros_tempranos'])
ax.set_xlabel("Tardanzas")
ax.set_ylabel("Retiros")
st.pyplot(fig)

# -----------------------
# SEGMENTACIÓN
# -----------------------
st.subheader("📊 Segmentación dinámica")
st.bar_chart(df_filtrado['segmento'].value_counts())

# -----------------------
# COMPARACIÓN POR PERIODO
# -----------------------
st.subheader("📈 Comparación por Periodo")

comparacion = df_filtrado.groupby('id_periodo')[['tardanzas','score']].mean()
st.line_chart(comparacion)

# -----------------------
# PARETO INTERACTIVO
# -----------------------
st.subheader("📊 Pareto dinámico")

ranking = df_filtrado.groupby('id_estudiante')['score'].sum().sort_values(ascending=False)
top = ranking.head(int(len(ranking)*0.2))

if len(ranking) > 0:
    porcentaje = top.sum() / ranking.sum()
    st.metric("Concentración", f"{round(porcentaje*100,2)}%")

st.bar_chart(ranking.head(10))

# -----------------------
# TABLA EXPLORABLE
# -----------------------
st.subheader("🔍 Explora los datos")

st.dataframe(df_filtrado, use_container_width=True)

# -----------------------
# INSIGHTS AUTOMÁTICOS
# -----------------------
st.subheader("🧠 Insights")

if df_filtrado['tardanzas'].mean() > 5:
    st.error("🚨 Problema serio de tardanzas")
elif df_filtrado['tardanzas'].mean() > 3:
    st.warning("⚠️ Nivel medio de tardanzas")
else:
    st.success("✅ Buen comportamiento")

# -----------------------
# EXPORTAR
# -----------------------
st.subheader("📥 Descargar datos filtrados")

csv = df_filtrado.to_csv(index=False)

st.download_button(
    "Descargar CSV",
    csv,
    "datos_filtrados.csv"
)
