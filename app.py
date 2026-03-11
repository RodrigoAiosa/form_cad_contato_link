import streamlit as st
import psycopg2
import uuid
from datetime import datetime
from zoneinfo import ZoneInfo
from urllib.parse import quote

# ── Config ────────────────────────────────────────────────────────────────────
HOST     = "pg-2e2874e2-rodrigoaiosa-skydatasoluction.l.aivencloud.com"
PORT     = "13191"
DATABASE = "BD_SKYDATA"
USER     = "avnadmin"
PASSWORD = "AVNS_LlZukuJoh_0Kbj0dhvK"
SSL_MODE = "require"

FUSO_BRASIL = ZoneInfo("America/Sao_Paulo")
BASE_URL    = "https://formcadcontatolink.streamlit.app/"

# ── Helpers ───────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(
        host=HOST, port=PORT, database=DATABASE,
        user=USER, password=PASSWORD, sslmode=SSL_MODE
    )

def salvar_cadastro(id_ref_proprio, url_indicacao, nome, cpf, sexo, email, whatsapp):
    """
    id_ref_proprio → ref único gerado para ESTA pessoa (aparece no link dela)
    url_indicacao  → ref de quem a indicou (vazio se veio direto)
    """
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO cad_contato_indicacao
            (id_ref_proprio, url_indicacao, nome, cpf, sexo, email, whatsapp, data_hora_cadastro)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        id_ref_proprio, url_indicacao,
        nome, cpf, sexo, email, whatsapp,
        datetime.now(FUSO_BRASIL)
    ))
    conn.commit()
    cursor.close()
    conn.close()

def formatar_cpf(cpf: str) -> str:
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) == 11:
        return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    return cpf

def formatar_whatsapp(w: str) -> str:
    return ''.join(filter(str.isdigit, w))

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); min-height: 100vh; }
section[data-testid="stSidebar"] { display: none; }
.card {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px; padding: 2.5rem 2rem; backdrop-filter: blur(12px);
    box-shadow: 0 8px 40px rgba(0,0,0,0.4); max-width: 560px; margin: 2rem auto;
}
.titulo { font-family: 'Space Mono', monospace; font-size: 1.7rem; font-weight: 700; color: #fff; text-align: center; letter-spacing: -1px; margin-bottom: 0.3rem; }
.subtitulo { color: rgba(255,255,255,0.5); text-align: center; font-size: 0.88rem; margin-bottom: 2rem; }
.ref-badge { background: rgba(99,102,241,0.2); border: 1px solid rgba(99,102,241,0.5); border-radius: 8px; padding: 0.6rem 1rem; font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #a5b4fc; text-align: center; margin-bottom: 1.5rem; word-break: break-all; }
.link-box { background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.4); border-radius: 12px; padding: 1.2rem; margin: 1rem 0; }
.link-titulo { color: #6ee7b7; font-size: 0.8rem; font-weight: 600; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 0.5rem; }
.link-url { font-family: 'Space Mono', monospace; font-size: 0.82rem; color: #fff; word-break: break-all; line-height: 1.5; }
.sucesso { color: #6ee7b7; text-align: center; font-weight: 600; font-size: 1.1rem; margin-bottom: 0.5rem; }
label, .stTextInput label, .stSelectbox label { color: rgba(255,255,255,0.75) !important; font-size: 0.85rem !important; }
input, .stTextInput input { background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 10px !important; color: #fff !important; }
div[data-baseweb="select"] > div { background: rgba(255,255,255,0.07) !important; border: 1px solid rgba(255,255,255,0.15) !important; border-radius: 10px !important; color: #fff !important; }
.stButton > button { width: 100%; background: linear-gradient(90deg, #6366f1, #8b5cf6) !important; color: #fff !important; border: none !important; border-radius: 12px !important; padding: 0.7rem 1.5rem !important; font-family: 'Sora', sans-serif !important; font-weight: 600 !important; font-size: 0.95rem !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.85 !important; }
.wpp-btn { display: inline-block; background: #25D366; color: #fff !important; text-decoration: none !important; padding: 0.65rem 1.4rem; border-radius: 12px; font-weight: 600; font-size: 0.9rem; text-align: center; width: 100%; box-sizing: border-box; margin-top: 0.5rem; }
.wpp-btn:hover { background: #1ebe57; }
hr { border-color: rgba(255,255,255,0.1); margin: 1.5rem 0; }
</style>
""", unsafe_allow_html=True)

# ── Lê ?ref= da URL (ref de quem enviou o link) ───────────────────────────────
params        = st.query_params
ref_indicador = params.get("ref", None)  # ref de quem me indicou

# ── Layout ────────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="titulo">📋 Cadastro</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitulo">Preencha seus dados para se cadastrar</div>', unsafe_allow_html=True)

if ref_indicador:
    st.markdown(
        f'<div class="ref-badge">🔗 Indicado por: {BASE_URL}?ref={ref_indicador}</div>',
        unsafe_allow_html=True
    )

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "cadastrado"   not in st.session_state: st.session_state.cadastrado   = False
if "link_proprio" not in st.session_state: st.session_state.link_proprio = ""

# ── Formulário ────────────────────────────────────────────────────────────────
if not st.session_state.cadastrado:
    nome     = st.text_input("Nome completo")
    cpf      = st.text_input("CPF", placeholder="000.000.000-00")
    sexo     = st.selectbox("Sexo", ["", "Masculino", "Feminino", "Prefiro não informar"])
    email    = st.text_input("E-mail")
    whatsapp = st.text_input("WhatsApp", placeholder="(11) 91234-5678")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("✅ Enviar cadastro"):
        erros = []
        if not nome.strip():     erros.append("Nome é obrigatório.")
        if not cpf.strip():      erros.append("CPF é obrigatório.")
        if not sexo:             erros.append("Selecione o sexo.")
        if not email.strip():    erros.append("E-mail é obrigatório.")
        if not whatsapp.strip(): erros.append("WhatsApp é obrigatório.")

        if erros:
            for e in erros:
                st.error(e)
        else:
            try:
                # Ref único gerado para ESTA pessoa — é o código do link dela
                novo_ref  = str(uuid.uuid4())[:8]
                novo_link = f"{BASE_URL}?ref={novo_ref}"

                salvar_cadastro(
                    id_ref_proprio = novo_ref,           # ref desta pessoa → vai no link dela
                    url_indicacao  = ref_indicador or "",# ref de quem a indicou (ou vazio)
                    nome           = nome.strip(),
                    cpf            = formatar_cpf(cpf),
                    sexo           = sexo,
                    email          = email.strip(),
                    whatsapp       = formatar_whatsapp(whatsapp)
                )

                st.session_state.link_proprio = novo_link
                st.session_state.cadastrado   = True
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

# ── Tela pós-cadastro ─────────────────────────────────────────────────────────
else:
    link    = st.session_state.link_proprio
    msg_wpp = quote(f"Olá! Me cadastrei e quero te indicar. Acesse pelo meu link: {link}")
    wpp_url = f"https://wa.me/?text={msg_wpp}"

    st.markdown('<div class="sucesso">🎉 Cadastro realizado com sucesso!</div>', unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("""
        <div class="link-titulo">🔗 Seu link de indicação</div>
        <p style="color:rgba(255,255,255,0.55);font-size:0.82rem;margin-bottom:0.8rem;">
            Compartilhe este link. Quando alguém se cadastrar por ele, você será identificado como indicador.
        </p>
    """, unsafe_allow_html=True)
    st.markdown(
        f'<div class="link-box">'
        f'<div class="link-titulo">Link</div>'
        f'<div class="link-url">{link}</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    st.code(link, language=None)
    st.markdown(
        f'<a class="wpp-btn" href="{wpp_url}" target="_blank">📲 Compartilhar no WhatsApp</a>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Novo cadastro"):
        st.session_state.cadastrado   = False
        st.session_state.link_proprio = ""
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
