import re
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

def validar_cpf(cpf: str) -> bool:
    """Valida CPF com dígitos verificadores."""
    nums = ''.join(filter(str.isdigit, cpf))
    if len(nums) != 11 or nums == nums[0] * 11:
        return False
    # 1º dígito
    soma = sum(int(nums[i]) * (10 - i) for i in range(9))
    d1 = (soma * 10 % 11) % 10
    if d1 != int(nums[9]):
        return False
    # 2º dígito
    soma = sum(int(nums[i]) * (11 - i) for i in range(10))
    d2 = (soma * 10 % 11) % 10
    return d2 == int(nums[10])

def validar_email(email: str) -> bool:
    """Valida formato de e-mail."""
    padrao = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(padrao, email.strip()))

def validar_whatsapp(w: str) -> bool:
    """Valida WhatsApp brasileiro: DDD (2 dígitos) + número (8 ou 9 dígitos)."""
    nums = ''.join(filter(str.isdigit, w))
    # Aceita com ou sem código do país (55)
    if len(nums) == 13 and nums.startswith('55'):
        nums = nums[2:]
    if len(nums) == 12 and nums.startswith('55'):
        nums = nums[2:]
    return bool(re.match(r'^[1-9]{2}9?\d{8}$', nums))

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Cadastro", page_icon="📋", layout="centered")

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

* { box-sizing: border-box; }

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background-color: #f0f4f8 !important;
}

section[data-testid="stSidebar"]       { display: none !important; }
header[data-testid="stHeader"]         { display: none !important; }
div[data-testid="stToolbar"]           { display: none !important; }
div[data-testid="stDecoration"]        { display: none !important; }
footer                                 { display: none !important; }

/* ── Wrapper central ── */
.main-wrapper {
    max-width: 580px;
    margin: 2rem auto 4rem auto;
}

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    border-radius: 20px 20px 0 0;
    padding: 2.8rem 2.5rem 2.2rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 180px; height: 180px;
    background: rgba(255,255,255,0.07);
    border-radius: 50%;
}

.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; left: -30px;
    width: 220px; height: 220px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}

.hero-icon {
    font-size: 2.8rem;
    margin-bottom: 0.5rem;
    display: block;
}

.hero-title {
    font-size: 1.75rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}

.hero-sub {
    font-size: 0.92rem;
    color: rgba(255,255,255,0.75);
    margin: 0;
    font-weight: 400;
}

/* ── Card body ── */
.form-body {
    background: #ffffff;
    border-radius: 0 0 20px 20px;
    padding: 2.2rem 2.5rem 2.5rem;
    box-shadow: 0 10px 40px rgba(79,70,229,0.10);
}

/* ── Badge indicação ── */
.badge-indicacao {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    background: #eef2ff;
    border: 1px solid #c7d2fe;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    margin-bottom: 1.6rem;
    font-size: 0.8rem;
    color: #4338ca;
    font-weight: 500;
    word-break: break-all;
}

.badge-indicacao span.dot {
    width: 8px; height: 8px;
    background: #6366f1;
    border-radius: 50%;
    flex-shrink: 0;
}

/* ── Divisor de seção ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin: 1.6rem 0 1rem 0;
}

/* ── Labels ── */
label, .stTextInput label, .stSelectbox label {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #374151 !important;
    margin-bottom: 4px !important;
}

/* ── Inputs ── */
input, .stTextInput input {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    font-size: 0.92rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    padding: 0.65rem 0.9rem !important;
    transition: border-color 0.2s !important;
}

input:focus, .stTextInput input:focus {
    border-color: #6366f1 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
    caret-color: #6366f1 !important;
    outline: none !important;
}

/* Highlight do campo ativo */
.stTextInput:focus-within {
    position: relative;
}

.stTextInput:focus-within label {
    color: #4f46e5 !important;
}

.stTextInput:focus-within input {
    border-color: #6366f1 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* Select ativo */
div[data-baseweb="select"]:focus-within > div {
    border-color: #6366f1 !important;
    background: #fff !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── Select ── */
div[data-baseweb="select"] > div {
    background: #f8fafc !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    color: #1e293b !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* ── Botão principal ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 1.5rem !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.2px !important;
    transition: all 0.2s !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    margin-top: 0.5rem !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}

/* ── Tela de sucesso ── */
.success-header {
    text-align: center;
    padding: 1.5rem 0 1rem;
}

.success-icon {
    font-size: 3.5rem;
    display: block;
    margin-bottom: 0.5rem;
}

.success-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0 0 0.3rem 0;
}

.success-sub {
    font-size: 0.88rem;
    color: #64748b;
    margin: 0;
}

.divider {
    height: 1px;
    background: #f1f5f9;
    margin: 1.5rem 0;
}

.link-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 0.6rem;
}

.link-card {
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}

.link-card-url {
    font-size: 0.83rem;
    color: #4f46e5;
    font-weight: 600;
    word-break: break-all;
    line-height: 1.5;
}

.wpp-btn {
    display: block;
    background: #22c55e;
    color: #fff !important;
    text-decoration: none !important;
    padding: 0.8rem 1.5rem;
    border-radius: 12px;
    font-weight: 700;
    font-size: 0.95rem;
    text-align: center;
    width: 100%;
    box-shadow: 0 4px 14px rgba(34,197,94,0.3);
    transition: all 0.2s;
}

.wpp-btn:hover {
    background: #16a34a;
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(34,197,94,0.4);
}

.footer-note {
    text-align: center;
    font-size: 0.75rem;
    color: #cbd5e1;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── Lê ?ref= da URL ───────────────────────────────────────────────────────────
params        = st.query_params
ref_indicador = params.get("ref", None)

# ── Estado da sessão ──────────────────────────────────────────────────────────
if "cadastrado"   not in st.session_state: st.session_state.cadastrado   = False
if "link_proprio" not in st.session_state: st.session_state.link_proprio = ""

# ══════════════════════════════════════════════════════════════════════════════
# FORMULÁRIO
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.cadastrado:

    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # Hero
    st.markdown("""
    <div class="hero">
        <span class="hero-icon">📋</span>
        <p class="hero-title">Cadastro</p>
        <p class="hero-sub">Preencha seus dados para se cadastrar</p>
    </div>
    """, unsafe_allow_html=True)

    # Body
    st.markdown('<div class="form-body">', unsafe_allow_html=True)

    # Badge indicação
    if ref_indicador:
        st.markdown(f"""
        <div class="badge-indicacao">
            <span class="dot"></span>
            Indicado por: {BASE_URL}?ref={ref_indicador}
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-label">Dados pessoais</div>', unsafe_allow_html=True)

    nome     = st.text_input("Nome completo", placeholder="Digite seu nome completo")
    cpf      = st.text_input("CPF", placeholder="000.000.000-00")

    col1, col2 = st.columns(2)
    with col1:
        sexo = st.selectbox("Sexo", ["", "Masculino", "Feminino", "Prefiro não informar"])

    st.markdown('<div class="section-label">Contato</div>', unsafe_allow_html=True)

    email    = st.text_input("E-mail", placeholder="seu@email.com")
    whatsapp = st.text_input("WhatsApp", placeholder="(11) 91234-5678")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Enviar cadastro →"):
        erros = []
        if not nome.strip():
            erros.append("⚠️ Nome é obrigatório.")
        if not cpf.strip():
            erros.append("⚠️ CPF é obrigatório.")
        elif not validar_cpf(cpf):
            erros.append("❌ CPF inválido. Verifique os dígitos informados.")
        if not sexo:
            erros.append("⚠️ Selecione o sexo.")
        if not email.strip():
            erros.append("⚠️ E-mail é obrigatório.")
        elif not validar_email(email):
            erros.append("❌ E-mail inválido. Use o formato: nome@dominio.com")
        if not whatsapp.strip():
            erros.append("⚠️ WhatsApp é obrigatório.")
        elif not validar_whatsapp(whatsapp):
            erros.append("❌ WhatsApp inválido. Use DDD + número (ex: 11 91234-5678)")

        if erros:
            for e in erros:
                st.error(e)
        else:
            try:
                novo_ref  = str(uuid.uuid4())[:8]
                novo_link = f"{BASE_URL}?ref={novo_ref}"

                salvar_cadastro(
                    id_ref_proprio = novo_ref,
                    url_indicacao  = ref_indicador or "",
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

    st.markdown('<p class="footer-note">Seus dados estão protegidos e não serão compartilhados.</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # form-body
    st.markdown('</div>', unsafe_allow_html=True)  # main-wrapper

# ══════════════════════════════════════════════════════════════════════════════
# TELA PÓS-CADASTRO
# ══════════════════════════════════════════════════════════════════════════════
else:
    link    = st.session_state.link_proprio
    msg_wpp = quote(f"Olá! Me cadastrei e quero te indicar. Acesse pelo meu link: {link}")
    wpp_url = f"https://wa.me/?text={msg_wpp}"

    st.markdown('<div class="main-wrapper">', unsafe_allow_html=True)

    # Hero verde
    st.markdown("""
    <div class="hero" style="background: linear-gradient(135deg, #059669 0%, #10b981 50%, #34d399 100%);">
        <span class="hero-icon">🎉</span>
        <p class="hero-title">Cadastro realizado!</p>
        <p class="hero-sub">Seu cadastro foi salvo com sucesso</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="form-body">', unsafe_allow_html=True)

    st.markdown("""
    <div class="link-section-label">🔗 Seu link de indicação</div>
    <p style="font-size:0.85rem;color:#64748b;margin:0 0 0.8rem 0;">
        Compartilhe este link. Quem se cadastrar por ele será vinculado a você.
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f'<div class="link-card"><div class="link-card-url">{link}</div></div>', unsafe_allow_html=True)

    st.code(link, language=None)

    st.markdown(f'<a class="wpp-btn" href="{wpp_url}" target="_blank">📲 &nbsp; Compartilhar no WhatsApp</a>', unsafe_allow_html=True)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    if st.button("← Novo cadastro"):
        st.session_state.cadastrado   = False
        st.session_state.link_proprio = ""
        st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
