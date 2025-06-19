import streamlit as st
import json
import os
import requests
from collections import Counter
from roleta_ia import RoletaIA
from streamlit_autorefresh import st_autorefresh

# --- Configurações ---
HISTORICO_PATH = "historico_resultados.json"
API_URL = "https://api.casinoscores.com/svc-evolution-game-events/api/xxxtreme/round-results?gameId=14"

# --- Inicialização da IA ---
if "roleta_ia" not in st.session_state:
    st.session_state.roleta_ia = RoletaIA()

# --- Carregar histórico salvo ---
def carregar_historico():
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r") as f:
            return json.load(f)
    return []

# --- Salvar histórico atualizado ---
def salvar_historico(historico):
    with open(HISTORICO_PATH, "w") as f:
        json.dump(historico, f)

# --- Buscar último resultado da API ---
def fetch_latest_result():
    try:
        response = requests.get(API_URL)
        data = response.json()
        if isinstance(data, list) and len(data) > 0:
            return int(data[0]['outcome']['number'])
    except Exception as e:
        print("Erro ao buscar resultado da API:", e)
    return None

# --- Interface Streamlit ---
st.set_page_config(page_title="Roleta IA", layout="wide")
st.title("🎯 Previsão Inteligente de Roleta")

# --- Autorefresh a cada novo sorteio detectado ---
st_autorefresh(interval=10000, key="auto_refresh")  # 10s

# --- Carregar histórico ao iniciar ---
if "historico" not in st.session_state:
    st.session_state.historico = carregar_historico()

# --- Inserção manual opcional ---
with st.expander("➕ Inserir manualmente números anteriores (máx. 100)"):
    numeros_texto = st.text_area("Digite até 100 números separados por espaço:", "")
    if st.button("Adicionar ao histórico"):
        try:
            numeros = list(map(int, numeros_texto.strip().split()))
            if len(numeros) > 100:
                st.warning("Você pode adicionar no máximo 100 números.")
            else:
                st.session_state.historico = numeros + st.session_state.historico
                salvar_historico(st.session_state.historico)
                st.success("Números adicionados ao histórico.")
        except ValueError:
            st.error("Formato inválido. Use apenas números separados por espaço.")

# --- Captura automática do novo número da roleta ---
ultimo_resultado = fetch_latest_result()
historico = st.session_state.historico

if ultimo_resultado is not None:
    if len(historico) == 0 or historico[-1] != ultimo_resultado:
        historico.append(ultimo_resultado)
        st.session_state.historico = historico
        salvar_historico(historico)

# --- Mostrar histórico atual (últimos 100) ---
with st.expander("📜 Histórico de Sorteios (últimos 100)"):
    st.write(" ".join(map(str, historico[-100:])))

# --- Previsão ---
previsoes = st.session_state.roleta_ia.prever_numeros(historico)
if previsoes:
    st.subheader("🔮 Números Previstos")
    st.success(" ".join(map(str, previsoes)))

    acertos = st.session_state.roleta_ia.contar_acertos(previsoes, historico[-1])
    if acertos:
        st.info(f"✅ Número(s) acertado(s): {' '.join(map(str, acertos))}")
    else:
        st.warning("❌ Nenhum acerto no último sorteio.")
else:
    st.info("Aguardando pelo menos 91 sorteios no histórico para iniciar as previsões.")

# --- Resetar histórico ---
if st.button("🔄 Resetar histórico"):
    st.session_state.historico = []
    salvar_historico([])
    st.success("Histórico resetado.")

# --- Rodapé personalizado ---
st.markdown("---")
st.markdown("🔧 Desenvolvido com IA para análise de padrões de roleta – versão 90+1")
