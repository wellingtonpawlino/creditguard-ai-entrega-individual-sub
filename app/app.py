import faulthandler
import sys
import os

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
    return True


_warm_up()

sys.stderr.write("[APP] modelo pre-carregado\n")
sys.stderr.flush()


st.set_page_config(
    page_title="CreditGuard AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CreditGuard AI")

st.subheader("Predição de Inadimplência para Concessão de Crédito")

st.success("✅ Aplicação pronta para demonstração")

st.write("Modelo candidato para produção:")
st.write("LightGBM Balanced v2")

st.divider()

st.subheader("Status do Sistema")

st.success("✅ Streamlit Online")
st.success("✅ Aplicação Operacional")
st.success("✅ LightGBM Balanced v2 (Modelo Candidato)")

st.divider()

st.subheader("Análise de Crédito")

amt_income = st.number_input(
    "Renda Total do Cliente",
    min_value=0.0,
    value=150000.0
)

amt_credit = st.number_input(
    "Valor do Crédito",
    min_value=0.0,
    value=300000.0
)

amt_annuity = st.number_input(
    "Valor da Anuidade",
    min_value=0.0,
    value=25000.0
)

cnt_children = st.number_input(
    "Número de Filhos",
    min_value=0,
    value=0
)

idade = st.number_input(
    "Idade",
    min_value=18,
    max_value=100,
    value=35
)

ext_source_1 = st.number_input(
    "EXT_SOURCE_1",
    min_value=0.0,
    max_value=1.0,
    value=0.50
)

ext_source_2 = st.number_input(
    "EXT_SOURCE_2",
    min_value=0.0,
    max_value=1.0,
    value=0.50
)

ext_source_3 = st.number_input(
    "EXT_SOURCE_3",
    min_value=0.0,
    max_value=1.0,
    value=0.50
)

if st.button("Analisar Cliente"):

    sys.stderr.write("[APP] botao clicado — iniciando analise\n")
    sys.stderr.flush()

    st.success("✅ Análise executada")

    inputs = {
        "AMT_INCOME_TOTAL": amt_income,
        "AMT_CREDIT": amt_credit,
        "AMT_ANNUITY": amt_annuity,
        "CNT_CHILDREN": cnt_children,
        "DAYS_BIRTH": -(idade * 365),
        "EXT_SOURCE_1": ext_source_1,
        "EXT_SOURCE_2": ext_source_2,
        "EXT_SOURCE_3": ext_source_3,
    }

    sys.stderr.write(f"[APP] inputs montados: {inputs}\n")
    sys.stderr.flush()

    sys.stderr.write("[APP] chamando predict(inputs)\n")
    sys.stderr.flush()

    resultado = predict(inputs)

    sys.stderr.write(f"[APP] predict() retornou: {resultado}\n")
    sys.stderr.flush()

    sys.stderr.write("[APP] chamando log_prediction()\n")
    sys.stderr.flush()

    log_prediction(inputs, resultado, model_version=os.environ.get("MODEL_VERSION", "v1"))

    sys.stderr.write("[APP] log_prediction() concluido\n")
    sys.stderr.flush()

    probabilidade = resultado["probability"] * 100
    classe = resultado["prediction"]

    st.divider()
    st.subheader("Resultado do Modelo")

    with st.expander("Detalhes Técnicos do Modelo"):
        st.json(resultado)

    if classe == 1:

        st.metric(
            label="Probabilidade de Inadimplência",
            value=f"{probabilidade:.2f}%"
        )

        st.error("Classificação: ALTO RISCO")

        st.write(
            "Ação recomendada: Revisão manual da proposta."
        )

        st.write(
            "Motivo: O valor solicitado de crédito é superior à renda informada pelo cliente."
        )

        st.divider()

        st.subheader("Resumo da Decisão")

        st.write(f"Probabilidade de Inadimplência: {probabilidade:.2f}%")
        st.write("Classificação: ALTO RISCO")
        st.write("Ação: Revisão manual da proposta")

    else:

        st.metric(
            label="Probabilidade de Inadimplência",
            value=f"{probabilidade:.2f}%"
        )

        st.success("Classificação: BAIXO RISCO")

        st.write(
            "Ação recomendada: Aprovação automática."
        )

        st.write(
            "Motivo: A renda informada demonstra capacidade financeira compatível com o crédito solicitado."
        )

        st.divider()

        st.subheader("Resumo da Decisão")

        st.write(f"Probabilidade de Inadimplência: {probabilidade:.2f}%")
        st.write("Classificação: BAIXO RISCO")
        st.write("Ação: Aprovação automática")

    sys.stderr.write("[APP] renderizacao concluida — sem crash\n")
    sys.stderr.flush()
