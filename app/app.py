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


# ── HELPERS ───────────────────────────────────────────────────────────────────
def _fmt(v: float) -> str:
    return "R$ " + f"{v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _alerta(tipo: str, texto: str) -> str:
    mapa = {
        "info":    ("alerta-info",    "ℹ️"),
        "atencao": ("alerta-atencao", "⚠️"),
        "critico": ("alerta-critico", "🚨"),
        "ok":      ("alerta-ok",      "✅"),
    }
    cls, icone = mapa.get(tipo, ("alerta-info", "ℹ️"))
    return f'<div class="{cls}">{icone} {texto}</div>'


def _kpi(label: str, valor: str, bench: str, status: str = "ok") -> str:
    return (
        f'<div class="kpi-card kpi-{status}">'
        f'<div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{valor}</div>'
        f'<div class="kpi-bench">{bench}</div>'
        f'</div>'
    )


# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>

/* ── Paleta exclusiva ──────────────────────────────────────────────────────── */
/* #F97316  laranja            */
/* #EA580C  laranja escuro     */
/* #1F2937  cinza escuro       */
/* #374151  cinza médio        */
/* #F3F4F6  cinza claro        */
/* #FFFFFF  branco             */
/* #DC2626  vermelho (alertas críticos e ALTO RISCO) */

/* ── Base ── */
.stApp { background-color: #F3F4F6; }

/* ── Labels dos campos de input ── */
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] label {
    color:         #F97316 !important;
    font-size:     14px !important;
    font-weight:   700 !important;
    opacity:       1 !important;
    margin-bottom: 0.1rem !important;
    line-height:   1.3 !important;
}

/* ── Espaçamento entre label, input e próxima seção ── */
.stNumberInput {
    margin-bottom: 0.85rem !important;
}
div[data-testid="column"] {
    padding-top: 0.3rem !important;
}

/* ── Caption (Faixa válida bureau) ── */
.stCaption p {
    color:       #374151 !important;
    font-size:   0.78rem !important;
    font-weight: 500 !important;
    opacity:     1 !important;
    margin-top:  0.1rem !important;
}

/* ── Botão primário ── */
.stButton > button[kind="primary"] {
    background-color: #374151 !important;
    border-color:     #374151 !important;
    color:            #FFFFFF !important;
    font-weight: 700;
    font-size:   1rem;
    padding:     0.65rem 1.5rem;
    border-radius: 8px;
    transition:  background 0.2s;
}
.stButton > button[kind="primary"]:hover {
    background-color: #1F2937 !important;
    border-color:     #1F2937 !important;
}

/* ── Header ── */
.header-container {
    background: linear-gradient(135deg, #1F2937 0%, #374151 100%);
    padding:       1.8rem 2rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    border-left:   6px solid #F97316;
}
.header-title { color: #FFFFFF; font-size: 1.9rem; font-weight: 800; margin: 0; }
.header-sub   { color: #D1D5DB; font-size: 0.95rem; margin-top: 0.25rem; }
.header-badge {
    display:          inline-block;
    background:       #F97316;
    color:            #FFFFFF;
    padding:          0.18rem 0.75rem;
    border-radius:    20px;
    font-size:        0.72rem;
    font-weight:      700;
    margin-top:       0.55rem;
    letter-spacing:   0.04em;
}

/* ── Títulos de seção ── */
.section-title {
    color:          #1F2937;
    font-size:      0.76rem;
    font-weight:    800;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    border-bottom:  2px solid #F97316;
    padding-bottom: 0.35rem;
    margin-bottom:  0.9rem;
    margin-top:     0.5rem;
}

/* ── Info box (Valor Total do Bem) ── */
.info-box {
    background:    #FFFFFF;
    border-left:   4px solid #F97316;
    padding:       0.7rem 1rem;
    border-radius: 0 8px 8px 0;
    color:         #374151;
    font-size:     0.88rem;
    margin:        0.5rem 0 1rem;
    box-shadow:    0 1px 3px rgba(0,0,0,0.06);
}

/* ── Alertas ── */
.alerta-info, .alerta-atencao, .alerta-critico, .alerta-ok {
    padding:       0.65rem 1rem;
    border-radius: 0 8px 8px 0;
    color:         #1F2937;
    font-size:     0.87rem;
    margin:        0.35rem 0;
    line-height:   1.45;
    font-weight:   500;
}
.alerta-info    { background: #FFF7ED; border-left: 4px solid #F97316; }
.alerta-atencao { background: #FFE7CC; border-left: 4px solid #EA580C; }
.alerta-critico { background: #FEE2E2; border-left: 4px solid #DC2626; }
.alerta-ok      { background: #F3F4F6; border-left: 4px solid #374151; }

/* ── Resumo da Operação — grid de cards ── */
.op-grid {
    display:               grid;
    grid-template-columns: 1fr 1fr;
    gap:                   0.5rem;
    margin-bottom:         0.9rem;
}
.op-item {
    background:    #FFFFFF;
    border-radius: 8px;
    padding:       0.65rem 0.85rem;
    box-shadow:    0 1px 3px rgba(0,0,0,0.07);
    border-top:    3px solid #F97316;
}
.op-label { font-size: 0.69rem; color: #374151; text-transform: uppercase; letter-spacing: 0.06em; }
.op-value { font-size: 0.95rem; font-weight: 700; color: #1F2937; margin-top: 0.15rem; }

/* ── KPI Cards (Indicadores) ── */
.kpi-grid {
    display:               grid;
    grid-template-columns: 1fr 1fr;
    gap:                   0.5rem;
    margin-bottom:         0.9rem;
}
.kpi-card {
    background:    #FFFFFF;
    border-radius: 8px;
    padding:       0.75rem 0.9rem;
    box-shadow:    0 1px 4px rgba(0,0,0,0.08);
    border-top:    3px solid #F3F4F6;
}
.kpi-ok      { border-top-color: #374151; }
.kpi-warn    { border-top-color: #F97316; }
.kpi-critico { border-top-color: #DC2626; }
.kpi-label { font-size: 0.69rem; color: #374151; text-transform: uppercase; letter-spacing: 0.06em; }
.kpi-value { font-size: 1.25rem; font-weight: 800; color: #1F2937; margin: 0.15rem 0 0.05rem; }
.kpi-bench { font-size: 0.71rem; color: #6B7280; }

/* ── Card principal de decisão ── */
.result-card {
    border-radius: 14px;
    padding:       2rem 1.8rem;
    text-align:    center;
    margin-bottom: 1rem;
    box-shadow:    0 6px 24px rgba(0,0,0,0.18);
}
.result-card-low  { background: linear-gradient(135deg, #14532D 0%, #16A34A 100%); }
.result-card-mid  { background: linear-gradient(135deg, #D97706 0%, #FBBF24 100%); }
.result-card-high { background: linear-gradient(135deg, #991B1B 0%, #DC2626 100%); }

.result-nivel      { font-size: 0.76rem; font-weight: 800; text-transform: uppercase;
                     letter-spacing: 0.14em; color: rgba(255,255,255,0.7); margin: 0; }
.result-emoji      { font-size: 2.2rem; margin: 0.4rem 0 0.1rem; }
.result-prob       { font-size: 3.4rem; font-weight: 900; color: #FFFFFF;
                     margin: 0; line-height: 1.05; }
.result-prob-label { font-size: 0.78rem; color: rgba(255,255,255,0.65); margin-bottom: 0.9rem; }
.result-divider    { border: none; border-top: 1px solid rgba(255,255,255,0.2); margin: 0.75rem 0; }
.result-acao       { font-size: 0.88rem; color: rgba(255,255,255,0.9); }

.prob-bar-track {
    background:    rgba(255,255,255,0.22);
    border-radius: 99px;
    height:        7px;
    margin:        0.5rem 0 0.3rem;
    overflow:      hidden;
}
.prob-bar-fill {
    height:        7px;
    border-radius: 99px;
}

/* ── Sidebar ── */
.sidebar-card {
    background:    #FFFFFF;
    border:        1px solid #F97316;
    border-radius: 10px;
    padding:       0.6rem 0.9rem;
    margin-bottom: 0.45rem;
    box-shadow:    0 2px 6px rgba(249,115,22,0.10);
}
.chip-label { font-size: 0.67rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.07em; }
.chip-value { font-size: 0.95rem; font-weight: 700; color: #1F2937; }

/* ── Rodapé ── */
.footer-bar {
    background:     #1F2937;
    border-radius:  8px;
    padding:        0.7rem 1.2rem;
    margin-top:     2rem;
    font-size:      0.78rem;
    color:          #9CA3AF;
    display:        flex;
    justify-content: space-between;
    flex-wrap:      wrap;
    gap:            0.5rem;
}
.footer-bar strong { color: #F97316; }

</style>
""", unsafe_allow_html=True)


# ── SIDEBAR ───────────────────────────────────────────────────────────────────
model_version = os.environ.get("MODEL_VERSION", "v2")
n_features    = len(_features_list)

with st.sidebar:
    st.markdown("### 🛡️ CreditGuard AI")
    st.markdown("---")

    st.markdown("**Status do Sistema**")
    for txt in ["✅ Modelo carregado", "✅ Aplicação operacional"]:
        st.markdown(
            f'<div class="sidebar-card"><div class="chip-value">{txt}</div></div>',
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("**Modelo em Produção**")
    for label, value in [
        ("Algoritmo",           "LightGBM Balanced"),
        ("Versão",              model_version),
        ("Features",            f"{n_features} variáveis"),
        ("ROC-AUC",             "0,7524"),
        ("Recall",              "66,06%"),
        ("Cobertura preditiva", "84,9% do gain"),
    ]:
        st.markdown(
            f'<div class="sidebar-card">'
            f'<div class="chip-label">{label}</div>'
            f'<div class="chip-value">{value}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

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


# ── LAYOUT PRINCIPAL ──────────────────────────────────────────────────────────
col_form, col_panel = st.columns([3, 2], gap="large")

with col_form:

    # — Dados Financeiros ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">💰 Dados Financeiros</p>', unsafe_allow_html=True)

    ff1, ff2 = st.columns(2)
    with ff1:
        amt_income = st.number_input(
            "Renda Anual do Cliente (R$)",
            min_value=0.0, value=150000.0, step=1000.0, format="%.2f",
            help="Renda anual bruta declarada (AMT_INCOME_TOTAL).",
        )
        amt_credit = st.number_input(
            "Valor do Crédito Solicitado (R$)",
            min_value=0.0, value=300000.0, step=1000.0, format="%.2f",
            help="Valor total do crédito solicitado (AMT_CREDIT).",
        )
    with ff2:
        amt_annuity = st.number_input(
            "Valor da Parcela Anual (R$)",
            min_value=0.0, value=25000.0, step=500.0, format="%.2f",
            help="Compromisso anual de pagamento do empréstimo (AMT_ANNUITY).",
        )
        down_payment = st.number_input(
            "Valor de Entrada (R$)",
            min_value=0.0, value=0.0, step=1000.0, format="%.2f",
            help="Valor pago pelo cliente com recursos próprios.",
        )

    valor_total_bem = amt_credit + down_payment
    st.markdown(
        f'<div class="info-box">💡 <strong>Valor Total do Bem:</strong> {_fmt(valor_total_bem)}'
        f'&nbsp;·&nbsp;Calculado como Crédito + Entrada</div>',
        unsafe_allow_html=True,
    )

    # — Perfil do Cliente ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">👤 Perfil do Cliente</p>', unsafe_allow_html=True)

    pf1, pf2, pf3 = st.columns(3)
    with pf1:
        idade = st.number_input(
            "Idade do Cliente", min_value=18, max_value=100, value=35,
            help="Idade em anos inteiros. Convertida internamente para DAYS_BIRTH = -(idade × 365).",
        )
    with pf2:
        tempo_emprego = st.number_input(
            "Tempo no Emprego Atual", min_value=0, max_value=60, value=5,
            help="Anos no emprego atual. Convertido internamente para DAYS_EMPLOYED = -(anos × 365).",
        )
    with pf3:
        cnt_children = st.number_input(
            "Número de Filhos", min_value=0, value=0,
            help="Filhos dependentes (CNT_CHILDREN).",
        )

    # — Scores de Crédito ──────────────────────────────────────────────────────
    st.markdown('<p class="section-title">📊 Scores de Crédito (Bureau 0 – 1)</p>', unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        ext_source_1 = st.number_input(
            "Score Bureau 1", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_1 — 3º maior preditor do modelo. 0,00 = risco máximo · 1,00 = risco mínimo.",
        )
    with sc2:
        ext_source_2 = st.number_input(
            "Score Bureau 2", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_2 — 2º maior preditor (gain 157.687). 0,00 = risco máximo · 1,00 = risco mínimo.",
        )
    with sc3:
        ext_source_3 = st.number_input(
            "Score Bureau 3", min_value=0.0, max_value=1.0, value=0.50, step=0.01, format="%.2f",
            help="EXT_SOURCE_3 — Maior preditor do modelo (gain 191.174). 0,00 = risco máximo · 1,00 = risco mínimo.",
        )
    st.caption("Faixa válida: 0,00 a 1,00  ·  0,00 = risco máximo  ·  0,50 = neutro  ·  1,00 = risco mínimo")


with col_panel:

    # Métricas derivadas
    renda_mensal  = amt_income / 12 if amt_income > 0 else 1.0
    ltv           = (amt_credit / valor_total_bem * 100) if valor_total_bem > 0 else 0.0
    debt_burden   = (amt_annuity / 12 / renda_mensal * 100) if renda_mensal > 0 else 0.0
    entrada_pct   = (down_payment / valor_total_bem * 100) if valor_total_bem > 0 else 0.0

    # — Resumo da Operação ─────────────────────────────────────────────────────
    st.markdown('<p class="section-title">📋 Resumo da Operação</p>', unsafe_allow_html=True)
    st.markdown(f"""
<div class="op-grid">
  <div class="op-item">
    <div class="op-label">Crédito Solicitado</div>
    <div class="op-value">{_fmt(amt_credit)}</div>
  </div>
  <div class="op-item">
    <div class="op-label">Entrada</div>
    <div class="op-value">{_fmt(down_payment)}</div>
  </div>
  <div class="op-item">
    <div class="op-label">Valor Total do Bem</div>
    <div class="op-value">{_fmt(valor_total_bem)}</div>
  </div>
  <div class="op-item">
    <div class="op-label">Parcela Mensal (est.)</div>
    <div class="op-value">{_fmt(amt_annuity / 12)}</div>
  </div>
  <div class="op-item">
    <div class="op-label">Parcela Anual</div>
    <div class="op-value">{_fmt(amt_annuity)}</div>
  </div>
  <div class="op-item">
    <div class="op-label">Renda Anual</div>
    <div class="op-value">{_fmt(amt_income)}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # — Indicadores ────────────────────────────────────────────────────────────
    st.markdown('<p class="section-title">📈 Indicadores</p>', unsafe_allow_html=True)

    ltv_st    = "ok" if ltv <= 80 else ("warn" if ltv <= 90 else "critico")
    debt_st   = "ok" if debt_burden <= 30 else ("warn" if debt_burden <= 40 else "critico")
    entr_st   = "ok" if entrada_pct >= 20 else ("warn" if entrada_pct >= 10 else "critico")
    emp_st    = "ok" if tempo_emprego >= 2 else ("warn" if tempo_emprego >= 1 else "critico")

    st.markdown(f"""
<div class="kpi-grid">
  {_kpi("LTV", f"{ltv:.0f}%", "Ideal: &lt; 80%", ltv_st)}
  {_kpi("Comprometimento", f"{debt_burden:.0f}%", "Ideal: &lt; 30%", debt_st)}
  {_kpi("Entrada (%)", f"{entrada_pct:.0f}%", "Ideal: &gt; 20%", entr_st)}
  {_kpi("Tempo de Emprego", f"{tempo_emprego} ano{'s' if tempo_emprego != 1 else ''}", "Ideal: &gt; 2 anos", emp_st)}
</div>
""", unsafe_allow_html=True)

    # — Alertas de Negócio ─────────────────────────────────────────────────────
    st.markdown('<p class="section-title">⚠️ Alertas</p>', unsafe_allow_html=True)

    alertas = []

    if amt_credit > amt_income:
        alertas.append(_alerta("atencao", "Crédito superior à renda anual informada."))
    if tempo_emprego < 1:
        alertas.append(_alerta("info", "Cliente com menos de 1 ano de emprego atual."))
    if amt_annuity > renda_mensal * 0.4:
        alertas.append(_alerta("critico", "Parcela representa mais de 40% da renda mensal."))
    if ltv > 90:
        alertas.append(_alerta("critico", f"LTV elevado ({ltv:.0f}%) — crédito cobre mais de 90% do bem."))
    elif ltv > 80:
        alertas.append(_alerta("atencao", f"LTV moderado ({ltv:.0f}%) — acima do ideal de 80%."))
    if down_payment >= amt_credit and down_payment > 0:
        alertas.append(_alerta("ok", "Entrada elevada em relação ao valor financiado."))
    if not alertas:
        alertas.append(_alerta("ok", "Nenhum alerta de negócio identificado."))

    st.markdown("\n".join(alertas), unsafe_allow_html=True)


# ── BOTÃO ─────────────────────────────────────────────────────────────────────
st.markdown("---")
analisar = st.button("🔍 Analisar Cliente", type="primary", use_container_width=True)

if analisar:

    sys.stderr.write("[APP] botao clicado — iniciando analise\n")
    sys.stderr.flush()

    amt_goods_price = amt_credit + down_payment

    inputs = {
        "AMT_INCOME_TOTAL": amt_income,
        "AMT_CREDIT":       amt_credit,
        "AMT_ANNUITY":      amt_annuity,
        "AMT_GOODS_PRICE":  amt_goods_price,
        "CNT_CHILDREN":     cnt_children,
        "DAYS_BIRTH":       -(idade * 365),
        "DAYS_EMPLOYED":    -(tempo_emprego * 365),
        "EXT_SOURCE_1":     ext_source_1,
        "EXT_SOURCE_2":     ext_source_2,
        "EXT_SOURCE_3":     ext_source_3,
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

    if probabilidade < 30:
        nivel       = "BAIXO RISCO"
        card_cls    = "result-card-low"
        emoji       = "✅"
        acao        = "Aprovação automática recomendada."
        prob_color  = "#DCFCE7"   # verde claro sobre fundo verde escuro
        bar_color   = "#4ADE80"   # verde médio — visível sobre track translúcido
        risk_color  = "#16A34A"   # borda superior dos KPI cards laterais
    elif probabilidade < 60:
        nivel       = "MÉDIO RISCO"
        card_cls    = "result-card-mid"
        emoji       = "⚠️"
        acao        = "Análise complementar recomendada."
        prob_color  = "#FEF9C3"   # amarelo muito claro — legível sobre amarelo escuro
        bar_color   = "#FCD34D"   # amarelo médio
        risk_color  = "#FBBF24"   # borda superior dos KPI cards laterais
    else:
        nivel       = "ALTO RISCO"
        card_cls    = "result-card-high"
        emoji       = "⛔"
        acao        = "Revisão manual obrigatória."
        prob_color  = "#FECACA"   # vermelho claro sobre fundo vermelho escuro
        bar_color   = "#F87171"   # vermelho médio
        risk_color  = "#DC2626"   # borda superior dos KPI cards laterais

    bar_pct = min(int(probabilidade), 100)

    st.markdown("### Resultado da Análise")

    res1, res2 = st.columns([2, 1])

    with res1:
        st.markdown(f"""
<div class="result-card {card_cls}">
  <p class="result-nivel">{nivel}</p>
  <p class="result-emoji">{emoji}</p>
  <p class="result-prob" style="color:{prob_color};">{probabilidade:.0f}%</p>
  <p class="result-prob-label">Probabilidade de Inadimplência</p>
  <div class="prob-bar-track">
    <div class="prob-bar-fill" style="width:{bar_pct}%; background:{bar_color};"></div>
  </div>
  <hr class="result-divider">
  <p class="result-acao">📋 <strong>Ação recomendada:</strong> {acao}</p>
</div>
""", unsafe_allow_html=True)

    with res2:
        st.markdown(f"""
<div class="kpi-card" style="text-align:center; margin-bottom:0.5rem; border-top:3px solid {risk_color};">
  <div class="kpi-label">Probabilidade</div>
  <div class="kpi-value" style="font-size:1.6rem; color:{risk_color};">{probabilidade:.0f}%</div>
</div>
<div class="kpi-card" style="text-align:center; border-top:3px solid {risk_color};">
  <div class="kpi-label">Classificação Binária</div>
  <div class="kpi-value">{"Inadimplente" if classe == 1 else "Adimplente"}</div>
</div>
""", unsafe_allow_html=True)

        with st.expander("🔧 Detalhes Técnicos"):
            st.json(resultado)
            st.json({
                "AMT_GOODS_PRICE_calculado": amt_goods_price,
                "AMT_GOODS_PRICE_formula":   f"{amt_credit} + {down_payment}",
                "DAYS_BIRTH":                -(idade * 365),
                "DAYS_EMPLOYED":             -(tempo_emprego * 365),
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
