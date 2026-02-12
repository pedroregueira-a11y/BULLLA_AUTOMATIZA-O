import streamlit as st
import re
from reportlab.platypus import SimpleDocTemplate, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO

st.set_page_config(page_title="TXT → PDF", layout="centered")

st.title("Conversor TXT para PDF")
st.write("MINISTÉRIO DA FAZENDA - INFORME PCC")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type=["txt"])

if uploaded_file:

    conteudo = uploaded_file.read()

    try:
        texto = conteudo.decode("utf-8")
    except UnicodeDecodeError:
        texto = conteudo.decode("cp1252")

    # 🔥 Remove caracteres invisíveis
    texto = re.sub(r'[\uE000-\uF8FF]', '', texto)
    texto = re.sub(r'[\x00-\x1F]', '', texto)

    linhas = texto.splitlines(True)

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

    # 🔥 Registrar fonte Unicode
    pdfmetrics.registerFont(TTFont('DejaVuSansMono', 'DejaVuSansMono.ttf'))

    style = ParagraphStyle(
        name="Normal",
        fontName="DejaVuSansMono",
        fontSize=7,
        leading=8,
    )

    buffer = BytesIO()

    # ✅ USANDO A4 NORMAL
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    elements = []

    for i, bloco in enumerate(blocos):
        texto_bloco = "".join(bloco)
        elements.append(Preformatted(texto_bloco, style))

        # 🔥 Adiciona quebra de página entre blocos
        if i < len(blocos) - 1:
            elements.append(PageBreak())

    doc.build(elements)

    st.success("PDF gerado com sucesso ✔")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
