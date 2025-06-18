from sklearn.ensemble import RandomForestClassifier
from collections import Counter
import numpy as np

def get_color(n):
    if n == 0:
        return -1
    return 1 if n in {
        1, 3, 5, 7, 9, 12, 14, 16, 18,
        19, 21, 23, 25, 27, 30, 32, 34, 36
    } else 0

def get_coluna(n):
    return (n - 1) % 3 + 1 if n != 0 else 0

def get_linha(n):
    return ((n - 1) // 3) + 1 if n != 0 else 0

def get_duzia(n):
    if n == 0:
        return 0
    return (n - 1) // 12 + 1

def extrair_features(numero, freq_norm, janela, idx_num, total_pares, total_impares):
    ultimos_tres = janela[max(0, idx_num - 3):idx_num]
    distancia_media = np.mean([abs(numero - x) for x in ultimos_tres]) if ultimos_tres else 0
    repetido = int(numero in ultimos_tres)

    features = [
        numero % 2,
        numero % 3,
        1 if 19 <= numero <= 36 else 0,
        get_color(numero),
        get_coluna(numero),
        get_linha(numero),
        get_duzia(numero),
        freq_norm.get(numero, 0),
        (numero - janela[idx_num-1]) if idx_num > 0 else 0,
        total_pares / len(janela),
        total_impares / len(janela),
        repetido,
        distancia_media
    ]
    return features

def construir_entrada(janela, freq, freq_total):
    freq_norm = {k: v / freq_total for k, v in freq.items()} if freq_total > 0 else {}
    total_pares = sum(1 for n in janela if n != 0 and n % 2 == 0)
    total_impares = sum(1 for n in janela if n != 0 and n % 2 == 1)
    features = []
    for i, n in enumerate(janela):
        feats = extrair_features(n, freq_norm, janela, i, total_pares, total_impares)
        features.extend(feats)
    return features

class ModeloIA:
    def __init__(self):
        self.modelo = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.classes_ = np.array(list(range(37)))
        self.iniciado = False

    def treinar(self, entradas, saidas):
        X = np.array(entradas)
        y = np.array(saidas)
        self.modelo.fit(X, y)
        self.iniciado = True

    def prever(self, entrada, top_k=4, prob_threshold=0.01):
        if not self.iniciado:
            return []
        proba = self.modelo.predict_proba([entrada])[0]
        candidatos = [(idx, p) for idx, p in enumerate(proba) if p >= prob_threshold]
        candidatos.sort(key=lambda x: x[1], reverse=True)
        top_indices = [idx for idx, p in candidatos[:top_k]]
        if len(top_indices) < top_k:
            top_restantes = np.argsort(proba)[::-1]
            for idx in top_restantes:
                if idx not in top_indices:
                    top_indices.append(idx)
                if len(top_indices) == top_k:
                    break
        return top_indices

class RoletaIA:
    def __init__(self, janela_min=18, janela_max=36):
        self.modelo = ModeloIA()
        self.janela_min = janela_min
        self.janela_max = janela_max

    def treinar_batch(self, numeros):
        entradas = []
        saidas = []
        for i in range(self.janela_max, len(numeros) - 1):
            janela_tamanho = min(self.janela_max, i)
            janela = numeros[i - janela_tamanho:i]
            saida = numeros[i]

            if any(n < 0 or n > 36 for n in janela + [saida]):
                continue

            freq = Counter(numeros[:i])
            freq_total = sum(freq.values())
            entrada = construir_entrada(janela, freq, freq_total)
            entradas.append(entrada)
            saidas.append(saida)

        if entradas and saidas:
            self.modelo.treinar(entradas, saidas)

    def prever_numeros(self, historico):
        numeros = [item["number"] for item in historico]
        if len(numeros) < self.janela_min + 1:
            return []
        self.treinar_batch(numeros)
        janela_recente = numeros[-self.janela_max:]
        freq_final = Counter(numeros[:-1])
        freq_total_final = sum(freq_final.values())
        entrada = construir_entrada(janela_recente, freq_final, freq_total_final)
        return self.modelo.prever(entrada)