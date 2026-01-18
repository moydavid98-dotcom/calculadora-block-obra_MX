    import streamlit as st
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# --------------------------------------------------
# CONFIGURACIÓN GENERAL
# --------------------------------------------------
st.set_page_config(
    page_title="CalcBlock MX",
    page_icon="🧱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🧱 Calculadora de Block y Ladrillo – Obra MX")
st.caption("Cálculo realista de materiales conforme a práctica común en México")

# --------------------------------------------------
# TIPO DE PIEZA
# --------------------------------------------------
st.subheader("🧱 Tipo de pieza")

tipo_pieza = st.selectbox(
    "Selecciona la pieza",
    ["Block 12", "Block 15", "Block 20", "Ladrillo rojo / tabique"]
)

if tipo_pieza == "Block 12":
    lb, hb, ab = 40.0, 20.0, 12.0
elif tipo_pieza == "Block 15":
    lb, hb, ab = 40.0, 20.0, 15.0
elif tipo_pieza == "Block 20":
    lb, hb, ab = 40.0, 20.0, 20.0
else:
    lb, hb, ab = 23.0, 5.0, 7.0

# --------------------------------------------------
# DIMENSIONES
# --------------------------------------------------
st.subheader("📐 Dimensiones de la pieza")

c1, c2 = st.columns(2)
with c1:
    lb = st.number_input("Largo (cm)", value=lb)
with c2:
    hb = st.number_input("Alto (cm)", value=hb)

ab = st.number_input("Espesor (cm)", value=ab)

# --------------------------------------------------
# JUNTA Y DESPERDICIO
# --------------------------------------------------
st.subheader("🧵 Junta y desperdicio")

c1, c2 = st.columns(2)
with c1:
    junta = st.number_input("Junta (cm)", value=1.0)
with c2:
    desperdicio = st.number_input("Desperdicio (%)", value=7.0)

# --------------------------------------------------
# MURO
# --------------------------------------------------
st.subheader("📐 Muro")

metodo = st.radio(
    "Cómo ingresar el muro",
    ["Área directa", "Medidas (largo × alto)"],
    horizontal=True
)

if metodo == "Área directa":
    area_muro = st.number_input("Área del muro (m²)", value=10.0)
else:
    c1, c2 = st.columns(2)
    with c1:
        largo_muro = st.number_input("Largo del muro (m)", value=5.0)
    with c2:
        alto_muro = st.number_input("Alto del muro (m)", value=2.5)

    area_muro = largo_muro * alto_muro
    st.metric("Área calculada", f"{area_muro:.2f} m²")

# --------------------------------------------------
# LIGANTE (LENGUAJE DE OBRA)
# --------------------------------------------------
st.subheader("🪣 Material para pegar")

tipo_ligante = st.radio(
    "Selecciona el material",
    [
        "Mortero (bultos 25 kg)",
        "Cemento + arena",
        "Ambos (mortero + cemento)"
    ]
)

# --------------------------------------------------
# CONFIGURACIÓN DE MATERIALES
# --------------------------------------------------
st.subheader("⚖ Configuración de materiales")

# Arena (siempre editable)
costo_arena = st.number_input("Costo arena ($/m³)", value=450.0)

# Cemento
costo_cemento = st.number_input("Costo bulto cemento 50 kg ($)", value=280.0)

# Mortero
costo_mortero = st.number_input("Costo bulto de mortero 25 kg ($)", value=120.0)
rendimiento_mortero = st.number_input(
    "Rendimiento por bulto de mortero (m³)",
    value=0.013
)

# Proporciones (si hay cemento)
if tipo_ligante in ["Cemento + arena", "Ambos (mortero + cemento)"]:
    c1, c2 = st.columns(2)
    with c1:
        cemento_partes = st.number_input("Partes de cemento", value=1)
    with c2:
        arena_partes = st.number_input("Partes de arena", value=4)

# --------------------------------------------------
# COSTO DE PIEZA
# --------------------------------------------------
with st.expander("💰 Costo de la pieza"):
    costo_pieza = st.number_input("Costo unitario ($)", value=18.0)

# --------------------------------------------------
# FUNCIÓN PDF
# --------------------------------------------------
def generar_pdf(datos):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    def linea(txt):
        nonlocal y
        c.drawString(40, y, txt)
        y -= 14

    c.setFont("Helvetica-Bold", 14)
    linea("CALCULADORA DE MATERIALES – OBRA (MX)")
    y -= 10

    c.setFont("Helvetica", 10)
    linea(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 15

    for k, v in datos.items():
        linea(f"- {k}: {v}")

    y -= 20
    c.setFont("Helvetica-Oblique", 8)
    linea("Cálculo aproximado conforme a práctica común de obra en México.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# CALCULAR
# --------------------------------------------------
st.markdown("---")
if st.button("🧮 CALCULAR", use_container_width=True):

    largo_mod = lb + junta
    alto_mod = hb + junta
    piezas_m2 = 10000 / (largo_mod * alto_mod)
    piezas = math.ceil(piezas_m2 * area_muro * (1 + desperdicio / 100))

    volumen_muro = area_muro * (ab / 100)
    volumen_pieza = (lb * hb * ab) / 1_000_000
    volumen_piezas = piezas * volumen_pieza
    volumen_ligante = volumen_muro - volumen_piezas

    costo_total = piezas * costo_pieza

    arena_m3 = 0
    cemento_bultos = 0
    mortero_bultos = 0

    if tipo_ligante == "Mortero (bultos 25 kg)":
        mortero_bultos = math.ceil(volumen_ligante / rendimiento_mortero)
        costo_total += mortero_bultos * costo_mortero

    elif tipo_ligante == "Cemento + arena":
        total_partes = cemento_partes + arena_partes
        vol_cemento = volumen_ligante * (cemento_partes / total_partes)
        arena_m3 = volumen_ligante * (arena_partes / total_partes)
        cemento_bultos = math.ceil(vol_cemento / 0.035)

        costo_total += cemento_bultos * costo_cemento
        costo_total += arena_m3 * costo_arena

    else:  # Ambos
        mitad = volumen_ligante / 2

        mortero_bultos = math.ceil(mitad / rendimiento_mortero)

        total_partes = cemento_partes + arena_partes
        vol_cemento = mitad * (cemento_partes / total_partes)
        arena_m3 = mitad * (arena_partes / total_partes)
        cemento_bultos = math.ceil(vol_cemento / 0.035)

        costo_total += mortero_bultos * costo_mortero
        costo_total += cemento_bultos * costo_cemento
        costo_total += arena_m3 * costo_arena

    # RESULTADOS
    st.subheader("🧱 Piezas")
    st.metric("Cantidad total", piezas)

    st.subheader("🪣 Materiales")
    if mortero_bultos:
        st.metric("Mortero 25 kg", f"{mortero_bultos} bultos")
    if cemento_bultos:
        st.metric("Cemento 50 kg", f"{cemento_bultos} bultos")
    if arena_m3:
        st.metric("Arena", f"{arena_m3:.2f} m³")

    st.subheader("💰 Costo total estimado")
    st.metric("Total", f"${costo_total:,.0f}")

    # PDF
    datos_pdf = {
        "Pieza": tipo_pieza,
        "Área del muro (m²)": f"{area_muro:.2f}",
        "Piezas": piezas,
        "Mortero (25 kg)": mortero_bultos,
        "Cemento (50 kg)": cemento_bultos,
        "Arena (m³)": f"{arena_m3:.2f}",
        "Costo total": f"${costo_total:,.0f}"
    }

    pdf = generar_pdf(datos_pdf)

    st.download_button(
        "📄 Exportar PDF",
        pdf,
        "calculo_materiales_obra_MX.pdf",
        "application/pdf",
        use_container_width=True
    )
