import faulthandler
import sys
import os
from datetime import datetime

faulthandler.enable(file=sys.stderr, all_threads=True)

sys.stderr.write("[APP] faulthandler ativo\n")
sys.stderr.flush()

sys.stderr.write("[APP] importando streamlit\n")
sys.stderr.flush()
import streamlit as st

sys.stderr.write("[APP] importando predict\n")
sys.stderr.flush()
sys.path.append("/app")
from Model.predict import predict, load_model, load_features

sys.stderr.write("[APP] importando log_prediction\n")
sys.stderr.flush()
from utils.db import log_prediction

sys.stderr.write("[APP] imports concluidos\n")
sys.stderr.flush()


@st.cache_resource
def _warm_up():
    sys.stderr.write("[APP] cache_resource: carregando modelo...\n")
    sys.stderr.flush()
    m = load_model()
    sys.stderr.write(f"[APP] cache_resource: modelo ok — {type(m)}\n")
    sys.stderr.flush()
    f = load_features()
    sys.stderr.write(f"[APP] cache_resource: {len(f)} features ok\n")
    sys.stderr.flush()
    return m, f


_model_obj, _features_list = _warm_up()

sys.stderr.write("[APP] modelo pre-carregado\n")
sys.stderr.flush()


st.set_page_config(
    page_title="CreditGuard AI",
    page_icon="🛡️",
    layout="wide"
)


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --orange: #F97316;
    --dark:   #374151;
    --light:  #F3F4F6;
    --bg:     #FAFAFA;
    --card:   #FFFFFF;
}

.stApp { background-color: var(--bg); }

/* Botão primário laranja */
.stButton > button[kind="primary"] {
    background-color: #F97316 !important;
    border-color: #F97316 !important;
    color: #FFFFFF !important;
    font-weight: 700;
    font-size: 1rem;
    padding: 0.6rem 1.5rem;
    border-radius: 8px;
}
.stButton > button[kind="primary"]:hover {
    background-color: #EA6C0A !important;
    border-color: #EA6C0A !important;
}

.header-container {
    background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
    padding: 1.8rem 2rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border-left: 6px solid #F97316;
}
.header-title { color: #FFFFFF; font-size: 1.9rem; font-weight: 800; margin: 0; }
.header-sub   { color: #D1D5DB; font-size: 0.95rem; margin-top: 0.25rem; }
.header-badge {
    display: inline-block;
    background: #F97316;
    color: #FFFFFF;
    padding: 0.18rem 0.75rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    margin-top: 0.55rem;
    letter-spacing: 0.04em;
}

.section-title {
    color: #374151;
    font-size: 0.78rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom: 2px solid #F97316;
    padding-bottom: 0.35rem;
    margin-bottom: 0.9rem;
    margin-top: 0.2rem;
}

.summary-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 1rem 1.3rem;
    margin-bottom: 0.9rem;
}
.summary-row {
    display: flex;
    justify-content: space-between;
    padding: 0.32rem 0;
    border-bottom: 1px solid #F3F4F6;
    font-size: 0.88rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-label { color: #6B7280; }
.summary-value { color: #374151; font-weight: 700; }

/* Cards de resultado */
.result-card {
    border-radius: 12px;
    padding: 1.6rem 1.8rem;
    text-align: center;
    margin-bottom: 1rem;
}
.result-low  { background: #D1FAE5; border: 2px solid #10B981; }
.result-mid  { background: #FEF3C7; border: 2px solid #F59E0B; }
.result-high { background: #FEE2E2; border: 2px solid #EF4444; }

.result-nivel { font-size: 1.5rem; font-weight: 800; margin: 0; }
.color-low  { color: #065F46; }
.color-mid  { color: #92400E; }
.color-high { color: #991B1B; }

.result-prob { font-size: 2.6rem; font-weight: 900; margin: 0.4rem 0 0.15rem; }
.result-sub  { color: #6B7280; font-size: 0.85rem; }
.result-acao { font-size: 0.9rem; margin-top: 0.6rem; }

.footer-bar {
    background: #F3F4F6;
    border-top: 1px solid #E5E7EB;
    padding: 0.7rem 1.2rem;
    border-radius: 8px;
    margin-top: 2rem;
    font-size: 0.78rem;
    color: #6B7280;
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 0.5rem;
}

.sidebar-chip {
    background: #F9FAFB;
    border-radius: 8px;
    padding: 0.55rem 0.9rem;
    margin-bottom: 0.45rem;
    border-left: 3px solid #F97316;
}
.chip-label { font-size: 0.7rem; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.06em; }
.chip-value { font-size: 0.95rem; font-weight: 700; color: #374151; }
</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
def _fmt(v):
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


model_version = os.environ.get("MODEL_VERSION", "v2")
n_features = len(_features_list)

with st.sidebar:
    st.markdown("### 🛡️ CreditGuard AI")
    st.markdown("---")

    st.markdown("**Status do Sistema**")
    st.success("✅ Modelo carregado")
    st.success("✅ Aplicação operacional")

    st.markdown("---")
    st.markdown("**Modelo em Produção**")
    st.markdown(f"""
<div class="sidebar-chip"><div class="chip-label">Algoritmo</div>
<div class="chip-value">LightGBM Balanced</div></div>
<div class="sidebar-chip"><div class="chip-label">Versão</div>
<div class="chip-value">{model_version}</div></div>
<div class="sidebar-chip"><div class="chip-label">Features</div>
<div class="chip-value">{n_features} variáveis</div></div>
<div class="sidebar-chip"><div class="chip-label">ROC-AUC</div>
<div class="chip-value">0,7524</div></div>
<div class="sidebar-chip"><div class="chip-label">Recall</div>
<div class="chip-value">66,06%</div></div>
<div class="sidebar-chip"><div class="chip-label">Cobertura preditiva</div>
<div class="chip-value">84,9% do gain</div></div>
""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Scores de Bureau (EXT_SOURCE)**")
    st.markdown("""
Os scores de bureau são avaliações normalizadas de risco emitidas por fontes externas de crédito independentes.

| Valor | Interpretação |
|---|---|
| **0,0** | Risco máximo |
| **0,5** | Risco neutro |
| **1,0** | Risco mínimo |

São os **3 maiores preditores** do modelo, respondendo por ~60% do poder preditivo total.
""")

    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")


# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-container">
    <div class="header-title">🛡️ CreditGuard AI</div>
    <div class="header-sub">Análise Inteligente de Risco de Crédito — ProScore Analytics</div>
    <span class="header-badge">LightGBM Balanced · 119 features · 84,9% cobertura preditiva</span>
</div>
""", unsafe_allow_html=True)


# ── FORMULÁRIO ────────────────────────────────────────────────────────────────
col_form, col_panel = st.columns([3, 2], gap="large")

with col_form:

    # — Dados Financeiros —
    st.markdown('<p class="section-title">💰 Dados Financeiros</p>', unsafe_allow_html=True)

    ff1, ff2 = st.columns(2)
    with ff1:
        amt_income = st.number_input(
            "Renda Anual do Cliente (R$)",
            min_value=0.0, value=150000.0, step=1000.0, format="%.2f",
            help="Renda anual bruta declarada (AMT_INCOME_TOTAL)."
        )
        amt_credit = st.number_input(
            "Valor do Crédito (R$)",
            min_value=0.0, value=300000.0, step=1000.0, format="%.2f",
            help="Valor total do crédito solicitado (AMT_CREDIT)."
        )
    with ff2:
        amt_annuity = st.number_input(
            "Valor da Parcela Anual (R$)",
            min_value=0.0, value=25000.0, step=500.0, format="%.2f",
            help="Compromisso anual de pagamento do empréstimo (AMT_ANNUITY)."
        )
        down_payment = st.number_input(
            "Valor de Entrada (R$)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f",
            help="Valor pago pelo cliente com recursos próprios."
        )

    valor_total_bem = amt_credit + down_payment
    st.info(f"💡 **Valor Total do Bem:** {_fmt(valor_total_bem)}  ·  Calculado como Crédito + Entrada")

    st.markdown("---")

    # — Perfil do Cliente —
    st.markdown('<p class="section-title">👤 Perfil do Cliente</p>', unsafe_allow_html=True)

    pf1, pf2, pf3 = st.columns(3)
    with pf1:
        idade = st.number_input(
            "Idade (anos)", min_value=18, max_value=100, value=35,
            help="Convertida para DAYS_BIRTH = -(idade × 365)."
        )
    with pf2:
        tempo_emprego = st.number_input(
            "Tempo de Emprego (anos)", min_value=0, max_value=60, value=5,
            help="Anos no emprego atual → DAYS_EMPLOYED = -(anos × 365)."
        )
    with pf3:
        cnt_children = st.number_input(
            "Nº de Filhos", min_value=0, value=0,
            help="Filhos dependentes (CNT_CHILDREN)."
        )

    st.markdown("---")

    # — Scores de Crédito —
    st.markdown('<p class="section-title">📊 Scores de Crédito (Bureau 0 – 1)</p>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        ext_source_1 = st.number_input(
            "Bureau 1", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_1 — 3º maior preditor do modelo."
        )
    with sc2:
        ext_source_2 = st.number_input(
            "Bureau 2", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_2 — 2º maior preditor (gain 157.687)."
        )
    with sc3:
        ext_source_3 = st.number_input(
            "Bureau 3", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_3 — Maior preditor do modelo (gain 191.174)."
        )


with col_panel:

    # — Resumo da Operação —
    st.markdown('<p class="section-title">📋 Resumo da Operação</p>', unsafe_allow_html=True)

    renda_mensal = amt_income / 12 if amt_income > 0 else 1.0

    st.markdown(f"""
<div class="summary-card">
  <div class="summary-row">
    <span class="summary-label">Crédito Solicitado</span>
    <span class="summary-value">{_fmt(amt_credit)}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">Entrada</span>
    <span class="summary-value">{_fmt(down_payment)}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">Valor Total do Bem</span>
    <span class="summary-value">{_fmt(valor_total_bem)}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">Parcela Anual</span>
    <span class="summary-value">{_fmt(amt_annuity)}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">Parcela Mensal (est.)</span>
    <span class="summary-value">{_fmt(amt_annuity / 12)}</span>
  </div>
  <div class="summary-row">
    <span class="summary-label">Renda Anual</span>
    <span class="summary-value">{_fmt(amt_income)}</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # — Indicadores Financeiros —
    st.markdown('<p class="section-title">📈 Indicadores</p>', unsafe_allow_html=True)

    ltv          = (amt_credit / valor_total_bem * 100) if valor_total_bem > 0 else 0.0
    debt_burden  = (amt_annuity / 12 / renda_mensal * 100) if renda_mensal > 0 else 0.0
    cred_renda   = (amt_credit / amt_income * 100) if amt_income > 0 else 0.0

    ind1, ind2 = st.columns(2)
    with ind1:
        st.metric("LTV", f"{ltv:.1f}%",
                  help="Crédito / Valor do Bem. Saudável abaixo de 80%.")
    with ind2:
        st.metric("Comprometimento", f"{debt_burden:.1f}%",
                  help="Parcela mensal / Renda mensal. Risco elevado acima de 30%.")

    # — Alertas de Negócio —
    st.markdown('<p class="section-title">⚠️ Alertas</p>', unsafe_allow_html=True)

    alertas = []

    if amt_credit > amt_income:
        st.warning("Crédito superior à renda anual informada.")
        alertas.append("credito_renda")

    if tempo_emprego < 1:
        st.info("Cliente com menos de 1 ano de emprego atual.")
        alertas.append("emprego")

    if amt_annuity > renda_mensal * 0.4:
        st.warning("Parcela representa mais de 40% da renda mensal.")
        alertas.append("parcela")

    if ltv > 90:
        st.warning(f"LTV elevado ({ltv:.1f}%) — crédito cobre mais de 90% do bem.")
        alertas.append("ltv")

    if down_payment >= amt_credit and down_payment > 0:
        st.success("Entrada elevada em relação ao valor financiado.")
        alertas.append("entrada_ok")

    if not alertas:
        st.success("✅ Nenhum alerta de negócio identificado.")


# ── BOTÃO DE ANÁLISE ──────────────────────────────────────────────────────────
st.markdown("---")
analisar = st.button("🔍 Analisar Cliente", type="primary", use_container_width=True)

if analisar:

    sys.stderr.write("[APP] botao clicado — iniciando analise\n")
    sys.stderr.flush()

    amt_goods_price = amt_credit + down_payment

    inputs = {
        "AMT_INCOME_TOTAL":  amt_income,
        "AMT_CREDIT":        amt_credit,
        "AMT_ANNUITY":       amt_annuity,
        "AMT_GOODS_PRICE":   amt_goods_price,
        "CNT_CHILDREN":      cnt_children,
        "DAYS_BIRTH":        -(idade * 365),
        "DAYS_EMPLOYED":     -(tempo_emprego * 365),
        "EXT_SOURCE_1":      ext_source_1,
        "EXT_SOURCE_2":      ext_source_2,
        "EXT_SOURCE_3":      ext_source_3,
    }

    sys.stderr.write(f"[APP] inputs: {inputs}\n")
    sys.stderr.flush()
    sys.stderr.write("[APP] chamando predict(inputs)\n")
    sys.stderr.flush()

    resultado = predict(inputs)

    sys.stderr.write(f"[APP] predict() retornou: {resultado}\n")
    sys.stderr.flush()

    log_prediction(inputs, resultado, model_version=os.environ.get("MODEL_VERSION", "v2"))

    sys.stderr.write("[APP] log_prediction() concluido\n")
    sys.stderr.flush()

    probabilidade = resultado["probability"] * 100
    classe        = resultado["prediction"]

    # Três níveis de risco
    if probabilidade < 30:
        nivel      = "BAIXO RISCO"
        card_cls   = "result-low"
        color_cls  = "color-low"
        emoji      = "✅"
        acao       = "Aprovação automática recomendada."
    elif probabilidade < 60:
        nivel      = "MÉDIO RISCO"
        card_cls   = "result-mid"
        color_cls  = "color-mid"
        emoji      = "⚠️"
        acao       = "Análise complementar recomendada antes da aprovação."
    else:
        nivel      = "ALTO RISCO"
        card_cls   = "result-high"
        color_cls  = "color-high"
        emoji      = "🚨"
        acao       = "Revisão manual da proposta obrigatória."

    st.markdown("### Resultado da Análise")

    res1, res2 = st.columns([2, 1])

    with res1:
        st.markdown(f"""
<div class="result-card {card_cls}">
  <p class="result-nivel {color_cls}">{emoji} {nivel}</p>
  <p class="result-prob {color_cls}">{probabilidade:.1f}%</p>
  <p class="result-sub">Probabilidade de Inadimplência</p>
  <p class="result-acao"><strong>Ação recomendada:</strong> {acao}</p>
</div>
""", unsafe_allow_html=True)

    with res2:
        st.markdown("**Gauge de Probabilidade**")
        st.progress(min(probabilidade / 100, 1.0))
        st.caption(f"{probabilidade:.1f}% de chance de inadimplência")

        st.markdown("---")
        st.metric("Probabilidade", f"{probabilidade:.1f}%")
        st.metric("Classificação Binária", "Inadimplente" if classe == 1 else "Adimplente")

        with st.expander("🔧 Detalhes Técnicos"):
            st.json(resultado)
            st.json({
                "AMT_GOODS_PRICE_calculado": amt_goods_price,
                "AMT_GOODS_PRICE_formula": f"{amt_credit} + {down_payment}",
                "DAYS_BIRTH": -(idade * 365),
                "DAYS_EMPLOYED": -(tempo_emprego * 365),
            })

    sys.stderr.write("[APP] renderizacao concluida — sem crash\n")
    sys.stderr.flush()


# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="footer-bar">
  <span>🤖 Modelo: <strong>LightGBM Balanced</strong></span>
  <span>📊 Features: <strong>{n_features}</strong></span>
  <span>🏷️ Versão: <strong>{model_version}</strong></span>
  <span>⚡ ProScore Analytics — CreditGuard AI</span>
</div>
""", unsafe_allow_html=True)
