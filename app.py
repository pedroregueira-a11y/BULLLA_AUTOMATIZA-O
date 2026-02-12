import streamlit as st
import re
from reportlab.platypus import SimpleDocTemplate, Preformatted, PageBreak
from reportlab.lib.styles import ParagraphStyle
from io import BytesIO

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="Conversor TXT → PDF",
    layout="wide"
)

# ===============================
# CSS PERSONALIZADO (PALHETA BULLLA)
# ===============================
st.markdown("""
    <style>
        body {
            background-color: #F4F6FA;
        }

        .stButton > button {
            background-color: #2F6BFF;
            color: white;
            border-radius: 8px;
            height: 3em;
            font-weight: 600;
            border: none;
            width: 100%;
        }

        .stButton > button:hover {
            background-color: #1f52d6;
        }

        .stFileUploader {
            border: 2px dashed #2F6BFF;
            padding: 20px;
            border-radius: 10px;
        }

        .block-container {
            padding-top: 2rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
    </style>
""", unsafe_allow_html=True)

# ===============================
# UPLOAD
# ===============================
uploaded_file = st.file_uploader(
    "Selecione o arquivo TXT",
    type=["txt"]
)

# ===============================
# PROCESSAMENTO
# ===============================
if uploaded_file:

    conteudo = uploaded_file.read()

    try:
        linhas = conteudo.decode("utf-8").splitlines(True)
    except:
        linhas = conteudo.decode("cp1252").splitlines(True)

    padrao_inicio = re.compile(
        r"M\sI\sN\sI\sS\sT\sE\sR\sI\sO\s+D\sA\s+F\sA\sZ\sE\sN\sD\sA"
    )

    blocos = []
    bloco_atual = []
    capturando = False

    for linha in linhas:
        if padrao_inicio.search(linha):
            if capturando and bloco_atual:
                blocos.append(bloco_atual)
                bloco_atual = []
            capturando = True

        if capturando:
            bloco_atual.append(linha)

    if bloco_atual:
        blocos.append(bloco_atual)

    if not blocos:
        st.error("Nenhum bloco 'MINISTERIO DA FAZENDA' encontrado.")
        st.stop()

    # ===============================
    # CONFIGURAÇÃO PDF
    # ===============================
    leading = 8
    fonte = 7

    style = ParagraphStyle(
        name="Normal",
        fontName="Courier",
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

    for i, bloco in enumerate(blocos):
        texto_bloco = "".join(bloco)
        elements.append(Preformatted(texto_bloco, style))

        if i < len(blocos) - 1:
            elements.append(PageBreak())

    doc.build(elements)

    st.success(f"PDF gerado com sucesso! ({len(blocos)} ministérios encontrados)")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
