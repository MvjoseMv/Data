import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# CONFIGURACIÓN
# -----------------------
st.set_page_config(page_title="Dashboard de Asistencia", layout="wide")

st.title("📊 Dashboard Inteligente de Asistencia Estudiantil")

# -----------------------
# CARGA DE DATOS
# -----------------------
@st.cache_data
def cargar_data():
    return pd.read_csv("asistencia_detalle.csv")

df = cargar_data()

# -----------------------
# FILTROS DINÁMICOS
# -----------------------
st.sidebar.header("🎛️ Filtros")

# Filtro por periodo
periodos = st.sidebar.multiselect(
    "Selecciona periodo",
    options=sorted(df['id_periodo'].unique()),
    default=sorted(df['id_periodo'].unique())
)

# Filtro por rango de tardanzas
rango_tardanzas = st.sidebar.slider(
    "Rango de tardanzas",
    int(df['tardanzas'].min()),
    int(df['tardanzas'].max()),
    (int(df['tardanzas'].min()), int(df['tardanzas'].max()))
)

# Aplicar filtros
df_filtrado = df[
    (df['id_periodo'].isin(periodos)) &
    (df['tardanzas'].between(rango_tardanzas[0], rango_tardanzas[1]))
].copy()

# -----------------------
# KPIs
# -----------------------
st.subheader("📌 Indicadores Clave")

col1, col2, col3 = st.columns(3)

col1.metric("Promedio Tardanzas", round(df_filtrado['tardanzas'].mean(), 2))
col2.metric("Promedio Retiros", round(df_filtrado['retiros_tempranos'].mean(), 2))
col3.metric("Total Registros", len(df_filtrado))

st.divider()

# -----------------------
# GRÁFICOS
# -----------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución de Tardanzas")
    fig, ax = plt.subplots()
    df_filtrado['tardanzas'].hist(ax=ax)
    ax.set_xlabel("Tardanzas")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

with col2:
    st.subheader("Distribución de Retiros Tempranos")
    fig, ax = plt.subplots()
    df_filtrado['retiros_tempranos'].hist(ax=ax)
    ax.set_xlabel("Retiros")
    ax.set_ylabel("Frecuencia")
    st.pyplot(fig)

# -----------------------
# RELACIÓN ENTRE VARIABLES
# -----------------------
st.subheader("Relación entre Tardanzas y Retiros")

fig, ax = plt.subplots()
ax.scatter(df_filtrado['tardanzas'], df_filtrado['retiros_tempranos'])
ax.set_xlabel("Tardanzas")
ax.set_ylabel("Retiros")
st.pyplot(fig)

# -----------------------
# SEGMENTACIÓN DE RIESGO
# -----------------------
def clasificar(t):
    if t <= 2:
        return "Bajo"
    elif t <= 5:
        return "Medio"
    else:
        return "Alto"

df_filtrado['nivel_riesgo'] = df_filtrado['tardanzas'].apply(clasificar)

st.subheader("Segmentación de Riesgo")
st.bar_chart(df_filtrado['nivel_riesgo'].value_counts())

# -----------------------
# ALERTAS
# -----------------------
st.subheader("🚨 Estudiantes en Riesgo")

alertas = df_filtrado[
    (df_filtrado['tardanzas'] > 5) |
    (df_filtrado['retiros_tempranos'] > 3)
]

st.dataframe(alertas)

# -----------------------
# TOP ESTUDIANTES
# -----------------------
st.subheader("🏆 Top 10 estudiantes con más tardanzas")

top = df_filtrado.groupby('id_estudiante')['tardanzas'] \
    .sum() \
    .sort_values(ascending=False) \
    .head(10)

st.bar_chart(top)

# -----------------------
# EXPORTAR DATOS
# -----------------------
st.subheader("📥 Exportar datos filtrados")

csv = df_filtrado.to_csv(index=False)

st.download_button(
    label="Descargar CSV",
    data=csv,
    file_name="datos_filtrados.csv",
    mime="text/csv"
)