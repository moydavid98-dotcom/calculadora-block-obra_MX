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
st.caption("Cálculo rápido conforme a práctica común de obra en México")

# --------------------------------------------------
# SELECTOR DE PIEZA
# --------------------------------------------------
st.subheader("🧱 Tipo de pieza")

tipo_pieza = st.selectbox(
    "Selecciona la pieza",
    ["Block 12", "Block 15", "Block 20", "Ladrillo rojo / tabique"]
)

# Valores típicos MX
if tipo_pieza == "Block 12":
    lb, hb, ab, peso_pieza = 40.0, 20.0, 12.0, 12.0
elif tipo_pieza == "Block 15":
    lb, hb, ab, peso_pieza = 40.0, 20.0, 15.0, 14.0
elif tipo_pieza == "Block 20":
    lb, hb, ab, peso_pieza = 40.0, 20.0, 20.0, 18.0
else:  # Ladrillo rojo
    lb, hb, ab, peso_pieza = 23.0, 5.0, 7.0, 3.0

# --------------------------------------------------
# DIMENSIONES (EDITABLES)
# --------------------------------------------------
st.subheader("📐 Dimensiones de la pieza")

c1, c2 = st.columns(2)
with c1:
    lb = st.number_input("Largo (cm)", value=lb)
with c2:
    hb = st.number_input("Alto (cm)", value=hb)

ab = st.number_input("Espesor (cm)", value=ab)
peso_pieza = st.number_input("Peso unitario (kg)", value=peso_pieza)

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
# TIPO DE MORTERO
# --------------------------------------------------
st.subheader("🪣 Tipo de mortero")

tipo_mortero = st.radio(
    "Selecciona el tipo de mortero",
    ["Premezclado (bultos 25 kg)", "Hecho en obra (cemento + arena)"]
)

# --------------------------------------------------
# CONFIG MORTERO
# --------------------------------------------------
if tipo_mortero == "Premezclado (bultos 25 kg)":
    rendimiento_mortero = st.number_input(
        "Rendimiento por bulto (m³)",
        value=0.013
    )
    costo_mortero_bulto = st.number_input(
        "Costo por bulto ($)",
        value=120.0
    )
else:
    c1, c2 = st.columns(2)
    with c1:
        cemento_partes = st.number_input("Cemento (partes)", value=1)
    with c2:
        arena_partes = st.number_input("Arena (partes)", value=4)

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
    linea("CALCULADORA DE BLOCK Y LADRILLO – OBRA (MX)")
    y -= 10

    c.setFont("Helvetica", 10)
    linea(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 15

    linea(f"Pieza: {datos['tipo_pieza']}")
    linea(f"Área del muro: {datos['area_muro']:.2f} m²")
    linea(f"Junta: {datos['junta']} cm")
    linea(f"Desperdicio: {datos['desperdicio']} %")
    y -= 10

    linea(f"Piezas totales: {datos['piezas']}")
    linea(f"Mortero: {datos['mortero']}")
    linea(f"Costo total: ${datos['costo_total']:,.0f}")

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

    # Cálculo de piezas
    largo_mod = lb + junta
    alto_mod = hb + junta

    piezas_m2 = 10000 / (largo_mod * alto_mod)
    piezas_net = piezas_m2 * area_muro
    piezas_tot = math.ceil(piezas_net * (1 + desperdicio / 100))

    # Volúmenes
    volumen_muro = area_muro * (ab / 100)
    volumen_pieza = (lb * hb * ab) / 1_000_000
    volumen_piezas = piezas_net * volumen_pieza
    volumen_mortero = volumen_muro - volumen_piezas

    costo_total = piezas_tot * costo_pieza

    st.subheader("🧱 Piezas")
    st.metric("Cantidad total", piezas_tot)

    st.subheader("🪣 Mortero")

    if tipo_mortero == "Premezclado (bultos 25 kg)":
        bultos_mortero = math.ceil(volumen_mortero / rendimiento_mortero)
        costo_mortero = bultos_mortero * costo_mortero_bulto
        st.metric("Mortero", f"{bultos_mortero} bultos (25 kg)")
        costo_total += costo_mortero
        mortero_txt = f"{bultos_mortero} bultos (25 kg)"
    else:
        total_partes = cemento_partes + arena_partes
        vol_cemento = volumen_mortero * (cemento_partes / total_partes)
        bultos_cemento = math.ceil(vol_cemento / 0.035)
        st.metric("Cemento", f"{bultos_cemento} bultos")
        mortero_txt = f"Cemento {bultos_cemento} bultos"

    st.subheader("💰 Costo total")
    st.metric("Total estimado", f"${costo_total:,.0f}")

    # PDF
    datos_pdf = {
        "tipo_pieza": tipo_pieza,
        "area_muro": area_muro,
        "junta": junta,
        "desperdicio": desperdicio,
        "piezas": piezas_tot,
        "mortero": mortero_txt,
        "costo_total": costo_total
    }

    pdf = generar_pdf(datos_pdf)

    st.download_button(
        "📄 Exportar PDF",
        pdf,
        "calculo_block_ladrillo_MX.pdf",
        "application/pdf",
        use_container_width=True
    )
