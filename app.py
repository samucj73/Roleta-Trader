import streamlit as st
import json
import os
import logging
import requests
from collections import Counter
from streamlit_autorefresh import st_autorefresh
from roleta_ia import RoletaIA, get_coluna, get_duzia
import numpy as np

HISTORICO_PATH = "historico_resultados.json"
API_URL = "https://api.casinoscores.com/svc-evolution-game-events/api/xxxtremelightningroulette/latest"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def fetch_latest_result():
    try:
        response = requests.get(API_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        data = response.json()
        game_data = data.get("data", {})
        result = game_data.get("result", {})
        outcome = result.get("outcome", {})
        lucky_list = result.get("luckyNumbersList", [])

        number = outcome.get("number")
        color = outcome.get("color", "-")
        timestamp = game_data.get("startedAt")
        lucky_numbers = [item["number"] for item in lucky_list]

        return {
            "number": number,
            "color": color,
            "timestamp": timestamp,
            "lucky_numbers": lucky_numbers
        }
    except Exception as e:
        logging.error(f"Erro ao buscar resultado da API: {e}")
        return None

def salvar_resultado_em_arquivo(history, caminho=HISTORICO_PATH):
    dados_existentes = []

    if os.path.exists(caminho):
        with open(caminho, "r") as f:
            try:
                dados_existentes = json.load(f)
            except json.JSONDecodeError:
                logging.warning("Arquivo JSON vazio ou corrompido. Recriando arquivo.")
                dados_existentes = []

    timestamps_existentes = {item['timestamp'] for item in dados_existentes if 'timestamp' in item}
    novos_filtrados = [item for item in history if item.get('timestamp') not in timestamps_existentes]
    dados_existentes.extend(novos_filtrados)
    dados_existentes.sort(key=lambda x: x.get('timestamp', 'manual'))

    with open(caminho, "w") as f:
        json.dump(dados_existentes, f, indent=2)

st.set_page_config(page_title="Roleta IA", layout="wide")
st.title("🎯 Previsão Inteligente de Roleta")

min_sorteios_para_prever = st.slider("Quantidade mínima de sorteios para previsão", 5, 100, 18)

st.subheader("✍️ Inserir até 100 Sorteios Anteriores Manualmente")
input_numbers = st.text_area("Digite os números separados por espaço (ex: 12 27 0 33 ...):", height=100)

if st.button("Adicionar Sorteios Manuais"):
    try:
        nums = [int(n.strip()) for n in input_numbers.split() if n.strip().isdigit() and 0 <= int(n.strip()) <= 36]
        if len(nums) > 100:
            st.warning("Você só pode inserir até 100 números.")
        else:
            for numero in nums:
                st.session_state.historico.append({
                    "number": numero,
                    "color": "-",
                    "timestamp": f"manual_{len(st.session_state.historico)}",
                    "lucky_numbers": []
                })
            salvar_resultado_em_arquivo(st.session_state.historico)
            st.success(f"{len(nums)} números adicionados ao histórico com sucesso.")
    except:
        st.error("Erro ao interpretar os números. Use apenas inteiros separados por espaço.")

count = st_autorefresh(interval=40000, limit=None, key="auto_refresh")

if "historico" not in st.session_state:
    if os.path.exists(HISTORICO_PATH):
        with open(HISTORICO_PATH, "r") as f:
            try:
                st.session_state.historico = json.load(f)
            except:
                st.session_state.historico = []
    else:
        st.session_state.historico = []

if "acertos" not in st.session_state:
    st.session_state.acertos = []

if "previsoes" not in st.session_state:
    st.session_state.previsoes = []

if "roleta_ia" not in st.session_state:
    st.session_state.roleta_ia = RoletaIA(janela_min=min_sorteios_para_prever)

resultado = fetch_latest_result()
ultimo_timestamp = (
    st.session_state.historico[-1]["timestamp"] if st.session_state.historico else None
)

if resultado and resultado["timestamp"] != ultimo_timestamp:
    novo_resultado = {
        "number": resultado["number"],
        "color": resultado["color"],
        "timestamp": resultado["timestamp"],
        "lucky_numbers": resultado["lucky_numbers"]
    }
    st.session_state.historico.append(novo_resultado)
    salvar_resultado_em_arquivo([novo_resultado])
    st.toast(f"🎲 Novo número capturado: {novo_resultado['number']}")
    previsoes = st.session_state.roleta_ia.prever_numeros(st.session_state.historico)
    st.session_state.previsoes = previsoes
    if resultado["number"] in previsoes:
        if resultado["number"] not in st.session_state.acertos:
            st.session_state.acertos.append(resultado["number"])
            st.toast(f"✅ Acerto! {resultado['number']} estava na previsão!")
else:
    st.info("⏳ Aguardando novo sorteio...")

st.subheader("🧾 Últimos Sorteios")
ultimos_numeros = " ".join(str(h["number"]) for h in st.session_state.historico[-10:])
st.write(f"Últimos sorteios: {ultimos_numeros}")

st.subheader("🔮 Previsão dos Próximos 4 Números")
if st.session_state.previsoes:
    previsoes_formatadas = " ".join(str(n) for n in st.session_state.previsoes)
    st.success(f"Previsões: {previsoes_formatadas}")
else:
    st.warning("Aguardando sorteios suficientes para iniciar...")

# Exibição dos padrões detectados
st.subheader("🧠 Padrões detectados no último sorteio analisado")
if len(st.session_state.historico) >= st.session_state.roleta_ia.janela_max:
    ultimo_num = st.session_state.historico[-1]["number"]
    anteriores = [h["number"] for h in st.session_state.historico[-4:-1]]
    padroes_detectados = []

    if ultimo_num % 2 == 0:
        padroes_detectados.append("Número par")
    else:
        padroes_detectados.append("Número ímpar")

    if ultimo_num >= 19:
        padroes_detectados.append("Número alto (19–36)")
    else:
        padroes_detectados.append("Número baixo (1–18)")

    col = get_coluna(ultimo_num)
    padroes_detectados.append(f"Coluna: {col}")

    duzia = get_duzia(ultimo_num)
    padroes_detectados.append(f"Dúzia: {duzia}")

    if ultimo_num in anteriores:
        padroes_detectados.append("Repetição recente (últimos 3)")

    distancias = [abs(ultimo_num - ant) for ant in anteriores]
    if distancias and np.mean(distancias) <= 3:
        padroes_detectados.append("Distância média baixa entre últimos números")

    for p in padroes_detectados:
        st.markdown(f"- {p}")
else:
    st.info("Padrões serão exibidos após sorteios suficientes.")

st.subheader("🏅 Acertos da IA")
col1, col2 = st.columns([4, 1])
with col1:
    if st.session_state.acertos:
        acertos_formatados = " ".join(str(n) for n in st.session_state.acertos)
        st.success(f"Acertos: {acertos_formatados}")
    else:
        st.info("Nenhum acerto.")
with col2:
    if st.button("Resetar Acertos"):
        st.session_state.acertos = []
        st.toast("Acertos resetados.")

st.subheader("📊 Taxa de Acertos")
total_prev = len([
    h for h in st.session_state.historico if h["number"] not in (None, 0)
]) - min_sorteios_para_prever
if total_prev > 0:
    acertos = len(st.session_state.acertos)
    taxa = acertos / total_prev * 100
    st.info(f"Taxa de acerto: {taxa:.2f}% ({acertos}/{total_prev})")
else:
    st.warning("Taxa será exibida após sorteios suficientes.")