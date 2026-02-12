import streamlit as st
import re
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from io import BytesIO

st.title("Conversor TXT → PDF (1 Ministério = 1 Página)")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type=["txt"])

if uploaded_file:

    # Tentar ler com utf-8 ou cp1252
    try:
        linhas = uploaded_file.read().decode("utf-8").splitlines(True)
    except:
        linhas = uploaded_file.read().decode("cp1252").splitlines(True)

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

    # Configuração PDF
    leading = 8
    fonte = 7

    style = ParagraphStyle(
        name="Normal",
        fontName="Courier",
        fontSize=fonte,
        leading=leading,
    )

    elements = []

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

    for bloco in blocos:
        texto_bloco = "".join(bloco)
        elements.append(Preformatted(texto_bloco, style))

    doc.build(elements)

    st.success("PDF gerado com sucesso!")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
