import streamlit as st
import re
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

st.set_page_config(page_title="TXT → PDF", layout="centered")

st.title("Conversor TXT para PDF")
st.write("MINISTÉRIO DA FAZENDA - INFORME PCC")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type=["txt"])

if uploaded_file:

    # ==============================
    # 1️⃣ LER E CORRIGIR ENCODING
    # ==============================
    conteudo = uploaded_file.read()

    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = conteudo.decode("cp1252")

    # ==============================
    # 2️⃣ LIMPAR CARACTERES INVISÍVEIS
    # ==============================
    texto = re.sub(r'[\uE000-\uF8FF]', '', texto)  # Private Use Area
    texto = re.sub(r'[\x00-\x1F]', '', texto)      # Caracteres controle

    linhas = texto.splitlines(True)

    # ==============================
    # 3️⃣ IDENTIFICAR BLOCOS
    # ==============================
    padrao_inicio = re.compile(
        r"M\s*I\s*N\s*I\s*S\s*T\s*E\s*R\s*I\s*O\s+D\s*A\s+F\s*A\s*Z\s*E\s*N\s*D\s*A"
    )

    blocos = []
    bloco_atual = []

    for linha in linhas:
        if padrao_inicio.search(linha) and bloco_atual:
            blocos.append(bloco_atual)
            bloco_atual = []
        bloco_atual.append(linha)

    if bloco_atual:
        blocos.append(bloco_atual)

    if not blocos:
        st.error("Nenhum bloco encontrado.")
        st.stop()

    # ==============================
    # 4️⃣ CONFIGURAÇÃO PDF
    # ==============================
    leading = 8
    fonte = 7

    # Registrar fonte Unicode (remove erro no Cloud)
    pdfmetrics.registerFont(TTFont('DejaVuSansMono', 'DejaVuSansMono.ttf'))

    style = ParagraphStyle(
        name="Normal",
        fontName="DejaVuSansMono",
        fontSize=fonte,
        leading=leading,
    )

    maior_bloco = max(len(bloco) for bloco in blocos)
    altura_total = (maior_bloco * leading) + 20
    largura_total = 600

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(largura_total, altura_total),
        rightMargin=5,
        leftMargin=5,
        topMargin=5,
        bottomMargin=5,
    )

    elements = []

    for bloco in blocos:
        texto_bloco = "".join(bloco)
        elements.append(Preformatted(texto_bloco, style))

    doc.build(elements)

    st.success("PDF gerado com sucesso ✔")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
