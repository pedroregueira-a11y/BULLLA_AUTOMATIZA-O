import streamlit as st
import re
import unicodedata
from reportlab.platypus import SimpleDocTemplate, Preformatted
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from io import BytesIO
import os

st.set_page_config(page_title="TXT → PDF", layout="centered")

st.title("Conversor TXT para PDF")
st.write("MINISTERIO DA FAZENDA INFORME PCC")

uploaded_file = st.file_uploader("Envie o arquivo .txt", type=["txt"])


# ==========================================
# 🔥 FUNÇÃO QUE REMOVE CARACTERES INVISÍVEIS
# ==========================================
def limpar_texto(texto):
    texto_limpo = []
    for ch in texto:
        categoria = unicodedata.category(ch)

        # Remove caracteres problemáticos
        # Cc = control
        # Cf = formatting
        # Co = private use
        # Cs = surrogate
        if categoria not in ("Cc", "Cf", "Co", "Cs"):
            texto_limpo.append(ch)

    return "".join(texto_limpo)


if uploaded_file:

    # =============================
    # LEITURA DO TXT
    # =============================
    conteudo = uploaded_file.read()

    try:
        linhas = conteudo.decode("utf-8").splitlines(True)
    except UnicodeDecodeError:
        linhas = conteudo.decode("cp1252").splitlines(True)

    # =============================
    # REGEX INICIO BLOCO
    # =============================
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

    # =============================
    # CONFIGURAÇÃO PDF
    # =============================
    leading = 8
    fonte = 7

    # 🔥 REGISTRA FONTE TTF (evita quadrados)
    if os.path.exists("DejaVuSansMono.ttf"):
        pdfmetrics.registerFont(
            TTFont("DejaVuMono", "DejaVuSansMono.ttf")
        )
        nome_fonte = "DejaVuMono"
    else:
        # fallback caso não encontre a fonte
        nome_fonte = "Courier"

    style = ParagraphStyle(
        name="Normal",
        fontName=nome_fonte,
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

    # =============================
    # GERA PDF
    # =============================
    for bloco in blocos:
        texto_bloco = "".join(bloco)

        # 🔥 LIMPA CARACTERES PROBLEMÁTICOS
        texto_bloco = limpar_texto(texto_bloco)

        elements.append(Preformatted(texto_bloco, style))

    doc.build(elements)

    st.success("PDF gerado com sucesso. Sem quadrados e sem caracteres invisíveis.")

    st.download_button(
        label="Baixar PDF",
        data=buffer.getvalue(),
        file_name="resultado.pdf",
        mime="application/pdf"
    )
