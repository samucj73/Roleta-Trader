import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime
import random
import io

st.set_page_config(page_title="Modo Trader Roleta", layout="wide", page_icon="🎰")

# Sessão inicial
if "historico" not in st.session_state:
    st.session_state.historico = []
if "banca" not in st.session_state:
    st.session_state.banca = 0.0
if "meta" not in st.session_state:
    st.session_state.meta = 0.0
if "stop" not in st.session_state:
    st.session_state.stop = 0.0

st.title("🎯 Modo Trader - Roleta Inteligente")

# Sidebar: Configurações
st.sidebar.header("Configurações Iniciais")
banca_inicial = st.sidebar.number_input("Banca Inicial (R$)", min_value=1.0, step=1.0, format="%.2f")
meta_percentual = st.sidebar.slider("Meta de Lucro (%)", 1, 100, 10)
stop_percentual = st.sidebar.slider("Stop Loss (%)", 1, 100, 10)

if st.sidebar.button("Iniciar Sessão"):
    st.session_state.banca = banca_inicial
    st.session_state.meta = banca_inicial * (1 + meta_percentual / 100)
    st.session_state.stop = banca_inicial * (1 - stop_percentual / 100)
    st.success("Sessão iniciada!")

# Entrada dos números sorteados
st.subheader("Últimos 100 números sorteados")
numeros_texto = st.text_area("Cole aqui os 100 últimos números (separados por vírgula)", height=100)
numeros_lista = []

if numeros_texto:
    try:
        numeros_lista = [int(x.strip()) for x in numeros_texto.split(",") if x.strip().isdigit()]
        if len(numeros_lista) != 100:
            st.warning("Por favor, insira exatamente 100 números.")
        else:
            df = pd.DataFrame(numeros_lista, columns=["Número"])
    except:
        st.error("Erro ao processar os números.")

# Painel da Banca
st.subheader("Painel da Banca")
col1, col2, col3 = st.columns(3)
col1.metric("Banca Atual", f"R$ {st.session_state.banca:.2f}")
col2.metric("Meta", f"R$ {st.session_state.meta:.2f}")
col3.metric("Stop", f"R$ {st.session_state.stop:.2f}")

# IA Simples (baseada em frequência)
if numeros_lista and len(numeros_lista) == 100:
    frequencia = pd.Series(numeros_lista).value_counts().sort_values(ascending=False)
    sugeridos = list(frequencia.head(3).index)

    st.subheader("Sugestão da IA")
    st.write(f"Números com maior chance: **{', '.join(map(str, sugeridos))}**")

    valor_aposta = st.number_input("Valor por número (R$)", min_value=1.0, step=1.0, value=2.0)

    if st.button("Apostar"):
        total_aposta = valor_aposta * len(sugeridos)
        resultado = random.randint(0, 36)
        ganhou = resultado in sugeridos

        if ganhou:
            ganho = valor_aposta * 12
            lucro = ganho - total_aposta
            st.session_state.banca += lucro
            resultado_texto = f"✅ Acertou! Número: {resultado} | Lucro: R$ {lucro:.2f}"
        else:
            prejuizo = total_aposta
            st.session_state.banca -= prejuizo
            resultado_texto = f"❌ Errou. Número: {resultado} | Prejuízo: R$ {prejuizo:.2f}"

        st.session_state.historico.insert(0, {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Números Sugeridos": sugeridos,
            "Número Sorteado": resultado,
            "Banca": round(st.session_state.banca, 2),
            "Resultado": "Vitória" if ganhou else "Derrota"
        })
        st.success(resultado_texto)

# Histórico
if st.session_state.historico:
    st.subheader("Histórico de Apostas")
    df_hist = pd.DataFrame(st.session_state.historico)
    st.dataframe(df_hist, use_container_width=True)

    # Exportação
    col1, col2, col3 = st.columns(3)
    with col1:
        csv = df_hist.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Baixar CSV", csv, "historico.csv", "text/csv")
    with col2:
        excel = io.BytesIO()
        df_hist.to_excel(excel, index=False, sheet_name="Histórico")
        st.download_button("⬇️ Baixar Excel", excel.getvalue(), "historico.xlsx", "application/vnd.ms-excel")
    with col3:
        st.download_button("⬇️ Baixar PDF", csv, "historico.pdf", "application/pdf")  # simplificado

# Estatísticas
if numeros_lista and len(numeros_lista) == 100:
    st.subheader("Estatísticas")
    col1, col2, col3 = st.columns(3)
    col1.metric("Mais Frequente", frequencia.idxmax())
    col2.metric("Menos Frequente", frequencia.idxmin())
    col3.metric("Moda", pd.Series(numeros_lista).mode()[0])

    st.markdown("**Frequência dos Números**")
    fig = go.Figure(data=[go.Bar(x=frequencia.index, y=frequencia.values)])
    fig.update_layout(xaxis_title="Número", yaxis_title="Frequência")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Outras Análises**")
    st.write(f"- Média: {np.mean(numeros_lista):.2f}")
    st.write(f"- Mediana: {np.median(numeros_lista):.2f}")
    st.write(f"- Desvio Padrão: {np.std(numeros_lista):.2f}")
    st.write(f"- % Pares: {np.mean([n % 2 == 0 for n in numeros_lista]) * 100:.1f}%")
    st.write(f"- % Ímpares: {np.mean([n % 2 != 0 for n in numeros_lista]) * 100:.1f}%")
    st.write(f"- % Altos (19-36): {np.mean([19 <= n <= 36 for n in numeros_lista]) * 100:.1f}%")
    st.write(f"- % Baixos (0-18): {np.mean([n <= 18 for n in numeros_lista]) * 100:.1f}%")
