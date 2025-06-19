import numpy as np
from sklearn.linear_model import SGDClassifier
from collections import Counter

class RoletaIA:
    def __init__(self):
        self.modelo = SGDClassifier(loss="log_loss", max_iter=1000, tol=1e-3)
        self.treinado = False

    def prever_numeros(self, historico):
        TAMANHO_JANELA = 90

        if len(historico) < TAMANHO_JANELA + 1:
            return []

        X = []
        y = []
        for i in range(len(historico) - TAMANHO_JANELA):
            X.append(historico[i:i+TAMANHO_JANELA])
            y.append(historico[i + TAMANHO_JANELA])

        X = np.array(X)
        y = np.array(y)

        try:
            self.modelo.fit(X, y)
            self.treinado = True
        except Exception as e:
            print("Erro ao treinar o modelo:", e)
            return []

        # Previsão com base nos últimos 90 números
        entrada = np.array(historico[-TAMANHO_JANELA:]).reshape(1, -1)
        try:
            probabilidades = self.modelo.predict_proba(entrada)[0]
            mais_provaveis = np.argsort(probabilidades)[-4:][::-1]
            return list(mais_provaveis)
        except Exception as e:
            print("Erro na previsão:", e)
            return []

    def contar_acertos(self, previsoes, ultimo_numero):
        return [n for n in previsoes if n == ultimo_numero]
