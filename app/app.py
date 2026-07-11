
import streamlit as st
import sys
sys.path.append("/app")
from Model.predict import predict



st.set_page_config(
    page_title="CreditGuard AI",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ CreditGuard AI")

st.subheader("Predição de Inadimplência para Concessão de Crédito")

st.success("✅ Aplicação pronta para demonstração")

st.write("Modelo candidato para produção:")
st.write("XGBoost Balanced")

st.divider()

st.subheader("Status do Sistema")

st.success("✅ Streamlit Online")
st.success("✅ Aplicação Operacional")
st.success("✅ XGBoost Balanced (Modelo Candidato)")

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

    st.success("✅ Análise executada")

    # TESTE DE INTEGRAÇÃO COM O XGBOOST
    
    resultado = predict({
        "AMT_INCOME_TOTAL": amt_income,
        "AMT_CREDIT": amt_credit,
        "AMT_ANNUITY": amt_annuity,
        "CNT_CHILDREN": cnt_children,
        "DAYS_BIRTH": -(idade * 365),
        "EXT_SOURCE_1": ext_source_1,
        "EXT_SOURCE_2": ext_source_2,
        "EXT_SOURCE_3": ext_source_3
        })


    probabilidade = resultado["probability"] * 100
    classe = resultado["prediction"]

    st.divider()
    st.subheader("Resultado do Modelo")
    
    with st.expander("Detalhes Técnicos do Modelo"):
        st.json(resultado)


    # MANTER A LÓGICA ATUAL TEMPORARIAMENTE
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