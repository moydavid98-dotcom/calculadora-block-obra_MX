import streamlit as st
import math
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------
st.set_page_config(
    page_title="Calculadora de Block – Obra MX",
    page_icon="🧱",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🧱 CALCULADORA DE BLOCK – OBRA (MX)")
st.caption("Cálculo conforme a práctica común de obra en México")

# --------------------------------------------------
# DATOS DEL BLOCK
# --------------------------------------------------
st.subheader("DATOS DEL BLOCK")

tipo_block = st.selectbox(
    "Tipo de block",
    ["Block 12", "Block 15", "Block 20", "Ladrillo rojo / tabique"]
)

if tipo_block == "Block 12":
    lb, hb, ab, peso_block = 38.0, 17.0, 12.0, 14.0
elif tipo_block == "Block 15":
    lb, hb, ab, peso_block = 38.0, 17.0, 15.0, 16.0
elif tipo_block == "Block 20":
    lb, hb, ab, peso_block = 38.0, 17.0, 20.0, 18.0
else:
    lb, hb, ab, peso_block = 23.0, 5.0, 7.0, 3.0

c1, c2 = st.columns(2)
with c1:
    lb = st.number_input("Largo (cm)", value=lb)
with c2:
    hb = st.number_input("Alto (cm)", value=hb)

ab = st.number_input("Espesor (cm)", value=ab)
junta = st.number_input("Junta (cm)", value=1.0)

# --------------------------------------------------
# MURO
# --------------------------------------------------
st.subheader("MURO")

metodo = st.radio(
    "Cómo ingresar el muro",
    ["Área directa", "Por dimensiones"],
    horizontal=True
)

if metodo == "Área directa":
    area_muro = st.number_input("Área del muro (m²)", value=112.92)
else:
    c1, c2 = st.columns(2)
    with c1:
        largo_muro = st.number_input("Largo del muro (m)", value=10.0)
    with c2:
        alto_muro = st.number_input("Alto del muro (m)", value=11.29)
    area_muro = largo_muro * alto_muro
    st.metric("Área calculada", f"{area_muro:.2f} m²")

desperdicio = st.number_input("Desperdicio (%)", value=5.0)

# --------------------------------------------------
# ADITIVO A EMPLEAR
# --------------------------------------------------
st.subheader("ADITIVO A EMPLEAR")

aditivo = st.radio(
    "Selecciona el aditivo",
    ["Mortero", "Cemento", "Ambos"],
    horizontal=True
)

st.subheader("PROPORCIÓN DE MEZCLA")

if aditivo in ["Mortero", "Cemento"]:
    c1, c2 = st.columns(2)
    with c1:
        p1 = st.number_input("Parte aditivo", value=1.0)
    with c2:
        p2 = st.number_input("Parte arena", value=1.0)
    total_partes = p1 + p2
else:
    c1, c2, c3 = st.columns(3)
    with c1:
        p1 = st.number_input("Mortero", value=1.0)
    with c2:
        p2 = st.number_input("Cemento", value=1.0)
    with c3:
        p3 = st.number_input("Arena", value=4.0)
    total_partes = p1 + p2 + p3

# --------------------------------------------------
# COSTOS UNITARIOS
# --------------------------------------------------
st.subheader("COSTOS UNITARIOS")

costo_block = st.number_input("Block ($/pza)", value=18.0)
costo_mortero = st.number_input("Mortero 25 kg ($)", value=190.0)
costo_cemento = st.number_input("Cemento 50 kg ($)", value=230.0)
costo_arena = st.number_input("Arena ($/m³)", value=450.0)

# --------------------------------------------------
# FUNCIÓN PDF
# --------------------------------------------------
def generar_pdf_reporte(d):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750

    def linea(txt, bold=False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 10)
        c.drawString(40, y, txt)
        y -= 14

    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, y, "CALCULADORA DE BLOCK – OBRA (MX)")
    y -= 30

    linea(f"Fecha: {d['fecha']}")
    y -= 15

    linea(f"DATOS DEL ({d['tipo_block']})", True)
    linea(f"- Dimensiones: {d['dimensiones']} cm")
    linea(f"- Junta: {d['junta']} cm")
    y -= 10

    linea("MURO", True)
    linea(f"- Área del muro: {d['area_muro']} m²")
    linea(f"- Desperdicio: {d['desperdicio']} %")
    y -= 10

    linea("RESULTADOS", True)
    linea(f"- Blocks netos: {d['blocks_netos']} pzas")
    linea(f"- Blocks con desperdicio: {d['blocks_totales']} pzas")
    if d["mortero_bultos"] > 0:
        linea(f"- Mortero (25 kg): {d['mortero_bultos']} bultos")
    if d["cemento_bultos"] > 0:
        linea(f"- Cemento (50 kg): {d['cemento_bultos']} bultos")
    if d["arena_m3"] > 0:
        linea(f"- Arena: {d['arena_m3']} m³")
    y -= 10

    linea("COSTOS", True)
    linea(f"- Blocks (${d['costo_block']} pza): ${d['costo_blocks']}")
    if d["mortero_bultos"] > 0:
        linea(f"- Mortero (${d['costo_mortero']}): ${d['costo_mortero_total']}")
    if d["cemento_bultos"] > 0:
        linea(f"- Cemento (${d['costo_cemento']}): ${d['costo_cemento_total']}")
    if d["arena_m3"] > 0:
        linea(f"- Arena (${d['costo_arena']} m³): ${d['costo_arena_total']}")
    linea(f"- TOTAL: ${d['costo_total']}")
    y -= 10

    linea("PESOS APROXIMADOS", True)
    linea(f"- Blocks: {d['peso_blocks']} kg")
    if d["mortero_bultos"] > 0:
        linea(f"- Mortero: {d['peso_mortero']} kg")
    if d["cemento_bultos"] > 0:
        linea(f"- Cemento: {d['peso_cemento']} kg")
    if d["arena_m3"] > 0:
        linea(f"- Arena: {d['peso_arena']} kg")

    y -= 20
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        40, y,
        "Cálculo aproximado conforme a práctica común de obra en México. "
        "No considera vanos, castillos ni cadenas."
    )

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# --------------------------------------------------
# CÁLCULO
# --------------------------------------------------
if st.button("🧮 CALCULAR", use_container_width=True):

    largo_mod = lb + junta
    alto_mod = hb + junta
    blocks_m2 = 10000 / (largo_mod * alto_mod)
    blocks_netos = blocks_m2 * area_muro
    blocks_totales = math.ceil(blocks_netos * (1 + desperdicio / 100))

    volumen_muro = area_muro * (ab / 100)
    volumen_block = (lb * hb * ab) / 1_000_000
    volumen_blocks = blocks_netos * volumen_block
    volumen_mezcla = volumen_muro - volumen_blocks

    mortero_bultos = cemento_bultos = 0
    arena_m3 = 0

    if aditivo == "Mortero":
        vol_m = (p1 / total_partes) * volumen_mezcla
        arena_m3 = (p2 / total_partes) * volumen_mezcla
        mortero_bultos = math.ceil(vol_m / 0.013)

    elif aditivo == "Cemento":
        vol_c = (p1 / total_partes) * volumen_mezcla
        arena_m3 = (p2 / total_partes) * volumen_mezcla
        cemento_bultos = math.ceil(vol_c / 0.035)

    else:
        vol_m = (p1 / total_partes) * volumen_mezcla
        vol_c = (p2 / total_partes) * volumen_mezcla
        arena_m3 = (p3 / total_partes) * volumen_mezcla
        mortero_bultos = math.ceil(vol_m / 0.013)
        cemento_bultos = math.ceil(vol_c / 0.035)

    costo_blocks = blocks_totales * costo_block
    costo_mort = mortero_bultos * costo_mortero
    costo_cem = cemento_bultos * costo_cemento
    costo_ar = arena_m3 * costo_arena
    costo_total = costo_blocks + costo_mort + costo_cem + costo_ar

    peso_blocks = blocks_totales * peso_block
    peso_mortero = mortero_bultos * 25
    peso_cemento = cemento_bultos * 50
    peso_arena = arena_m3 * 1600

    st.subheader("RESULTADOS")
    st.write(f"Blocks netos: **{math.ceil(blocks_netos)} pzas**")
    st.write(f"Blocks con desperdicio: **{blocks_totales} pzas**")
    if mortero_bultos:
        st.write(f"Mortero (25 kg): **{mortero_bultos} bultos**")
    if cemento_bultos:
        st.write(f"Cemento (50 kg): **{cemento_bultos} bultos**")
    if arena_m3:
        st.write(f"Arena: **{arena_m3:.2f} m³**")

    st.subheader("COSTOS")
    st.write(f"Blocks: ${costo_blocks:,.0f}")
    if mortero_bultos:
        st.write(f"Mortero: ${costo_mort:,.0f}")
    if cemento_bultos:
        st.write(f"Cemento: ${costo_cem:,.0f}")
    if arena_m3:
        st.write(f"Arena: ${costo_ar:,.0f}")
    st.write(f"**TOTAL: ${costo_total:,.0f}**")

    st.subheader("PESOS APROXIMADOS")
    st.write(f"Blocks: {peso_blocks:,.0f} kg")
    if mortero_bultos:
        st.write(f"Mortero: {peso_mortero:,.0f} kg")
    if cemento_bultos:
        st.write(f"Cemento: {peso_cemento:,.0f} kg")
    if arena_m3:
        st.write(f"Arena: {peso_arena:,.0f} kg")

    datos_pdf = {
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "tipo_block": tipo_block,
        "dimensiones": f"{lb} x {hb} x {ab}",
        "junta": junta,
        "area_muro": f"{area_muro:.2f}",
        "desperdicio": desperdicio,
        "blocks_netos": math.ceil(blocks_netos),
        "blocks_totales": blocks_totales,
        "mortero_bultos": mortero_bultos,
        "cemento_bultos": cemento_bultos,
        "arena_m3": f"{arena_m3:.2f}",
        "costo_block": f"{costo_block:.2f}",
        "costo_blocks": f"{costo_blocks:,.0f}",
        "costo_mortero": f"{costo_mortero:.2f}",
        "costo_mortero_total": f"{costo_mort:,.0f}",
        "costo_cemento": f"{costo_cemento:.2f}",
        "costo_cemento_total": f"{costo_cem:,.0f}",
        "costo_arena": f"{costo_arena:.2f}",
        "costo_arena_total": f"{costo_ar:,.0f}",
        "costo_total": f"{costo_total:,.0f}",
        "peso_blocks": f"{peso_blocks:,.0f}",
        "peso_mortero": f"{peso_mortero:,.0f}",
        "peso_cemento": f"{peso_cemento:,.0f}",
        "peso_arena": f"{peso_arena:,.0f}",
    }

    pdf = generar_pdf_reporte(datos_pdf)

    st.download_button(
        "📄 Exportar PDF",
        pdf,
        "calculo_block_obra_MX.pdf",
        "application/pdf",
        use_container_width=True
    )
