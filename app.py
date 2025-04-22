import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import random

# Inicialização da sessão
if 'banca' not in st.session_state:
    st.session_state.banca = 100.0
if 'historico' not in st.session_state:
    st.session_state.historico = []

st.set_page_config(page_title="Modo Trader - Roleta", layout="centered")

st.title("🎯 Modo Trader - Roleta")

# Configurações da aposta
meta_diaria = 0.10  # 10%
stop_loss = -0.10  # -10%
valor_por_numero = 2.0
numeros_apostados = [13, 22, 31]
ganho_por_acerto = 12.0  # lucro bruto por número

st.subheader("Status da Banca")
col1, col2, col3 = st.columns(3)
col1.metric("Banca Atual", f"R$ {st.session_state.banca:.2f}")
col2.metric("Meta Diária", "+10%")
col3.metric("Stop Loss", "-10%")

# Simulação de aposta
st.subheader("Próxima Aposta")
st.markdown(f"**Sugestão da IA:** {', '.join(map(str, numeros_apostados))}")
st.markdown(f"**Valor por número:** R$ {valor_por_numero:.2f}")

if st.button("Executar Aposta"):
    aposta_total = valor_por_numero * len(numeros_apostados)
    numero_sorteado = random.randint(0, 36)
    ganhou = numero_sorteado in numeros_apostados

    if ganhou:
        lucro = ganho_por_acerto - aposta_total
        st.session_state.banca += lucro
        resultado = f"✅ Acertou! Número: {numero_sorteado} | Lucro: R$ {lucro:.2f}"
    else:
        prejuizo = aposta_total
        st.session_state.banca -= prejuizo
        resultado = f"❌ Errou. Número: {numero_sorteado} | Prejuízo: R$ {prejuizo:.2f}"

    st.session_state.historico.insert(0, {
        'banca': st.session_state.banca,
        'numero': numero_sorteado,
        'ganhou': ganhou,
        'resultado': resultado
    })

# Histórico
st.subheader("Histórico")
for item in st.session_state.historico[:10]:
    st.markdown(f"- {item['resultado']}")

# Gráfico da evolução da banca
st.subheader("Evolução da Banca")
if st.session_state.historico:
    df = pd.DataFrame(st.session_state.historico[::-1])
    fig = go.Figure()
    fig.add_trace(go.Scatter(y=df['banca'], mode='lines+markers', name='Banca'))
    fig.update_layout(height=300, xaxis_title="Rodadas", yaxis_title="Banca (R$)")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Ainda não há dados para o gráfico. Execute uma aposta para começar.")
