import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# -----------------------
# CONFIGURACIÓN
# -----------------------
st.set_page_config(page_title="Dashboard Ejecutivo", layout="wide")

# -----------------------
# ESTILO VISUAL
# -----------------------
st.markdown("""
<style>
.metric-box {
    padding: 15px;
    border-radius: 10px;
    text-align: center;
    color: white;
    font-size: 18px;
}
.good {background-color: #28a745;}
.medium {background-color: #ffc107;}
.bad {background-color: #dc3545;}
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Ejecutivo de Asistencia")

# -----------------------
# CARGA DE DATOS
# -----------------------
@st.cache_data
def cargar_data():
    return pd.read_csv("asistencia_detalle.csv")

df = cargar_data()

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
st.sidebar.header("🎛️ Filtros")

periodos = st.sidebar.multiselect(
    "Periodo",
    df['id_periodo'].unique(),
    default=df['id_periodo'].unique()
)

df_filtrado = df[df['id_periodo'].isin(periodos)]

# -----------------------
# KPIs CON SEMÁFORO
# -----------------------
st.subheader("📌 Indicadores Clave")

col1, col2, col3, col4 = st.columns(4)

tardanzas_prom = df_filtrado['tardanzas'].mean()

if tardanzas_prom < 3:
    color = "good"
elif tardanzas_prom < 5:
    color = "medium"
else:
    color = "bad"

col1.markdown(f'<div class="metric-box {color}">Tardanzas<br>{round(tardanzas_prom,2)}</div>', unsafe_allow_html=True)
col2.metric("Retiros Promedio", round(df_filtrado['retiros_tempranos'].mean(),2))
col3.metric("Score Promedio", round(df_filtrado['score'].mean(),2))
col4.metric("Casos Críticos", len(df_filtrado[df_filtrado['segmento']=="Crítico"]))

st.divider()

# -----------------------
# INSIGHTS AUTOMÁTICOS
# -----------------------
st.subheader("🧠 Insights Automáticos")

if tardanzas_prom > 5:
    st.error("🚨 Alto nivel de tardanzas: requiere intervención inmediata")
elif tardanzas_prom > 3:
    st.warning("⚠️ Nivel medio de tardanzas")
else:
    st.success("✅ Buen control de asistencia")

# -----------------------
# GRÁFICOS ORDENADOS
# -----------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribución de Tardanzas")
    fig, ax = plt.subplots()
    df_filtrado['tardanzas'].hist(ax=ax)
    st.pyplot(fig)

with col2:
    st.subheader("Distribución del Score")
    fig, ax = plt.subplots()
    df_filtrado['score'].hist(ax=ax)
    st.pyplot(fig)

# -----------------------
# SEGMENTACIÓN
# -----------------------
st.subheader("📊 Segmentación de Estudiantes")
st.bar_chart(df_filtrado['segmento'].value_counts())

# -----------------------
# PARETO
# -----------------------
st.subheader("📊 Análisis Pareto")

ranking = df_filtrado.groupby('id_estudiante')['score'].sum().sort_values(ascending=False)
top_20 = ranking.head(int(len(ranking)*0.2))
porcentaje = top_20.sum() / ranking.sum()

st.metric("Concentración del problema", f"{round(porcentaje*100,2)}%")

# -----------------------
# TENDENCIA
# -----------------------
st.subheader("📈 Tendencia")

tendencia = df.groupby('id_periodo')['score'].mean()
st.line_chart(tendencia)

# -----------------------
# ALERTAS
# -----------------------
st.subheader("🚨 Estudiantes Críticos")

alertas = df_filtrado[df_filtrado['segmento']=="Crítico"]
st.dataframe(alertas)

# -----------------------
# TOP
# -----------------------
st.subheader("🏆 Top 10 Estudiantes")

st.bar_chart(ranking.head(10))

# -----------------------
# DESCARGA
# -----------------------
st.subheader("📥 Exportar")

csv = df_filtrado.to_csv(index=False)
st.download_button("Descargar CSV", csv, "datos.csv")
