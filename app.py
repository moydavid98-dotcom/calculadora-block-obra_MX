import streamlit as st
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime

# -----------------------
# CONFIGURACIÓN GENERAL
# -----------------------
st.set_page_config(
    page_title="CalcBlock MX",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🧱 Calculadora de Block – Obra MX")
st.caption("Cálculo rápido para obra, alineado a práctica común en México")

# -----------------------
# BLOCK
# -----------------------
st.subheader("🧱 Block")

c1, c2 = st.columns(2)
with c1:
    lb = st.number_input("Largo (cm)", value=40.0)
with c2:
    hb = st.number_input("Alto (cm)", value=20.0)

ab = st.number_input("Ancho (cm)", value=15.0)

# -----------------------
# JUNTA Y DESPERDICIO
# -----------------------
st.subheader("🧵 Junta y desperdicio")

c1, c2 = st.columns(2)
with c1:
    junta = st.number_input("Junta (cm)", value=1.0)
with c2:
    desperdicio = st.number_input(
        "Desperdicio (%)",
        min_value=0.0,
        max_value=20.0,
        value=5.0,
        help="En obra mexicana se usa normalmente 5–10 %"
    )

# -----------------------
# MURO
# -----------------------
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

# -----------------------
# MEZCLA
# -----------------------
st.subheader("🪣 Mezcla de mortero")

c1, c2 = st.columns(2)
with c1:
    cemento_partes = st.number_input("Cemento (partes)", value=1)
with c2:
    arena_partes = st.number_input("Arena (partes)", value=4)

total_partes = cemento_partes + arena_partes
st.caption("Proporciones comunes en México: 1:3, 1:4, 1:5")

# -----------------------
# COSTOS Y PESOS
# -----------------------
with st.expander("💰 Costos y pesos (opcional)"):
    c1, c2 = st.columns(2)
    with c1:
        costo_block = st.number_input("Costo block ($)", value=18.0)
        peso_block = st.number_input("Peso block (kg)", value=14.0)
    with c2:
        costo_cemento = st.number_input("Costo bulto cemento ($)", value=280.0)
        peso_cemento = st.number_input("Peso bulto cemento (kg)", value=50.0)

    costo_arena = st.number_input("Costo arena ($/m³)", value=450.0)
    peso_arena = st.number_input("Peso arena (kg/m³)", value=1600.0)

# -----------------------
# FUNCIÓN PDF
# -----------------------
def generar_pdf(datos):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    def texto(linea):
        nonlocal y
        c.drawString(40, y, linea)
        y -= 14

    c.setFont("Helvetica-Bold", 14)
    texto("CALCULADORA DE BLOCK – OBRA (MX)")
    y -= 10

    c.setFont("Helvetica", 10)
    texto(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    y -= 15

    texto("DATOS DEL BLOCK")
    texto(f"- Dimensiones: {datos['lb']} × {datos['hb']} × {datos['ab']} cm")
    texto(f"- Junta: {datos['junta']} cm")
    y -= 10

    texto("MURO")
    texto(f"- Área del muro: {datos['area_muro']:.2f} m²")
    texto(f"- Desperdicio: {datos['desperdicio']} %")
    y -= 10

    texto("RESULTADOS")
    texto(f"- Blocks netos: {datos['blocks_netos']}")
    texto(f"- Blocks con desperdicio: {datos['blocks_totales']}")
    texto(f"- Mortero total: {datos['vol_mortero']:.2f} m³")
    texto(f"- Cemento: {datos['bultos']} bultos")
    texto(f"- Arena: {datos['vol_arena']:.2f} m³")
    y -= 10

    texto("COSTOS")
    texto(f"- Blocks: ${datos['costo_blocks']:,.0f}")
    texto(f"- Cemento: ${datos['costo_cemento']:,.0f}")
    texto(f"- Arena: ${datos['costo_arena']:,.0f}")
    texto(f"- TOTAL: ${datos['costo_total']:,.0f}")
    y -= 10

    texto("PESOS APROXIMADOS")
    texto(f"- Blocks: {datos['peso_blocks']:,.0f} kg")
    texto(f"- Cemento: {datos['peso_cemento']:,.0f} kg")
    texto(f"- Arena: {datos['peso_arena']:,.0f} kg")

    y -= 20
    c.setFont("Helvetica-Oblique", 8)
    texto("Cálculo aproximado conforme a práctica común de obra en México.")
    texto("No considera vanos, castillos ni cadenas.")

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# -----------------------
# CALCULAR
# -----------------------
st.markdown("---")
if st.button("🧮 CALCULAR", use_container_width=True):

    # Medidas modulares
    largo_mod = lb + junta
    alto_mod = hb + junta

    blocks_m2 = 10000 / (largo_mod * alto_mod)
    blocks_netos = blocks_m2 * area_muro
    blocks_totales = blocks_netos * (1 + desperdicio / 100)

    # Volúmenes
    volumen_muro = area_muro * (ab / 100)
    volumen_block = (lb * hb * ab) / 1_000_000
    volumen_blocks = blocks_netos * volumen_block
    volumen_mortero = volumen_muro - volumen_blocks

    # Mortero
    vol_cemento = volumen_mortero * (cemento_partes / total_partes)
    vol_arena = volumen_mortero * (arena_partes / total_partes)
    bultos = math.ceil(vol_cemento / 0.035)

    # Costos
    costo_blocks = math.ceil(blocks_totales) * costo_block
    costo_cemento_total = bultos * costo_cemento
    costo_arena_total = vol_arena * costo_arena
    costo_total = costo_blocks + costo_cemento_total + costo_arena_total

    # Pesos
    peso_blocks_total = math.ceil(blocks_totales) * peso_block
    peso_cemento_total = bultos * peso_cemento
    peso_arena_total = vol_arena * peso_arena

    # -----------------------
    # RESULTADOS
    # -----------------------
    st.subheader("🧱 Blocks")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Netos", math.ceil(blocks_netos))
    with c2:
        st.metric("Con desperdicio", math.ceil(blocks_totales))

    st.subheader("🪣 Mortero")
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Cemento", f"{bultos} bultos")
    with c2:
        st.metric("Arena", f"{vol_arena:.2f} m³")

    st.subheader("💰 Costo total")
    st.metric("Total", f"${costo_total:,.0f}")

    # -----------------------
    # PDF
    # -----------------------
    datos_pdf = {
        "lb": lb,
        "hb": hb,
        "ab": ab,
        "junta": junta,
        "area_muro": area_muro,
        "desperdicio": desperdicio,
        "blocks_netos": math.ceil(blocks_netos),
        "blocks_totales": math.ceil(blocks_totales),
        "vol_mortero": volumen_mortero,
        "bultos": bultos,
        "vol_arena": vol_arena,
        "costo_blocks": costo_blocks,
        "costo_cemento": costo_cemento_total,
        "costo_arena": costo_arena_total,
        "costo_total": costo_total,
        "peso_blocks": peso_blocks_total,
        "peso_cemento": peso_cemento_total,
        "peso_arena": peso_arena_total
    }

    pdf = generar_pdf(datos_pdf)

    st.download_button(
        label="📄 Exportar PDF",
        data=pdf,
        file_name="calculo_block_obra_MX.pdf",
        mime="application/pdf",
        use_container_width=True
    )

    st.caption(
        "Resultados aproximados. No considera vanos, castillos ni cadenas."
    )
