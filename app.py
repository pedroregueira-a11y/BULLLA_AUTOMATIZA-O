import streamlit as st
import re
from reportlab.platypus import SimpleDocTemplate, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO

st.set_page_config(page_title="TXT → PDF", layout="centered")

st.title("Conversor TXT para PDF")
st.write("MINISTERIO DA FAZENDA INFORME PCC")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type=["txt"])

if uploaded_file:

    # ==========================
    # LER ARQUIVO
    # ==========================

    conteudo = uploaded_file.read()

    try:
        linhas = conteudo.decode("utf-8").splitlines(True)
    except UnicodeDecodeError:
        linhas = conteudo.decode("cp1252").splitlines(True)

    # ==========================
    # BLOCO (MESMO REGEX)
    # ==========================

    padrao_inicio = re.compile(
        r"M\sI\sN\sI\sS\sT\sE\sR\sI\sO\s+D\sA\s+F\sA\sZ\sE\sN\sD\sA"
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

    # ==========================
    # CONFIG
    # ==========================

    leading = 8
    fonte = 7

    style = ParagraphStyle(
        name="Normal",
        fontName="Courier",
        fontSize=fonte,
        leading=leading,
    )

    largura_total = 600
    altura_total = 842  # altura padrão A4 retrato

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=(largura_total, altura_total),
        rightMargin=5,
        leftMargin=5,
        topMargin=5,
        bottomMargin=5,
    )

    # ==========================
    # GERAR PDF
    # ==========================

    elements = []

    for i, bloco in enumerate(blocos):

        texto_bloco = "".join(bloco)
        texto_bloco = texto_bloco.replace("\r", "").replace("\x00", "")

        elements.append(Preformatted(texto_bloco, style))

        # 🔥 GARANTE 1 BLOCO = 1 PÁGINA
        if i < len(blocos) - 1:
            elements.append(PageBreak())

    doc.build(elements)

    st.success("PDF gerado com 1 Ministério = 1 página.")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
