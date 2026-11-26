"""Abordagem fuzzy (Mamdani): o grau de 'parecer cabra' vem de regras sobre saturação e brilho."""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from comum import carregar_hsv, limpar, salvar

# 1) Variáveis linguísticas e termos fuzzy (fuzzificação).
universo = np.arange(256)
saturacao = ctrl.Antecedent(universo, "saturacao")
brilho = ctrl.Antecedent(universo, "brilho")
cabra = ctrl.Consequent(np.arange(101), "cabra")

saturacao["baixa"] = fuzz.trapmf(universo, [0, 0, 40, 90])
saturacao["media"] = fuzz.trimf(universo, [40, 90, 150])
saturacao["alta"] = fuzz.trapmf(universo, [100, 170, 255, 255])
brilho["escuro"] = fuzz.trapmf(universo, [0, 0, 50, 110])
brilho["medio"] = fuzz.trimf(universo, [60, 130, 200])
brilho["claro"] = fuzz.trapmf(universo, [150, 210, 255, 255])
cabra["nao"] = fuzz.trimf(cabra.universe, [0, 0, 45])
cabra["talvez"] = fuzz.trimf(cabra.universe, [25, 50, 75])
cabra["sim"] = fuzz.trimf(cabra.universe, [55, 100, 100])

# 2) Base de regras.
regras = [
    ctrl.Rule(saturacao["baixa"] & brilho["claro"], cabra["sim"]),   # pelo branco ao sol
    ctrl.Rule(saturacao["baixa"] & brilho["medio"], cabra["sim"]),   # pelo branco na sombra
    ctrl.Rule(saturacao["baixa"] & brilho["escuro"], cabra["talvez"]),
    ctrl.Rule(saturacao["media"] & ~brilho["escuro"], cabra["talvez"]),
    ctrl.Rule(saturacao["alta"], cabra["nao"]),                      # grama verde, corda
    ctrl.Rule(brilho["escuro"] & ~saturacao["baixa"], cabra["nao"]),
]
sistema = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))

# 3) Inferência + defuzzificação (centróide). Como S e V vão de 0 a 255, calculamos
#    uma tabela 256x256 uma única vez e depois só consultamos cada pixel nela.
s, v = np.meshgrid(universo, universo, indexing="ij")
sistema.input["saturacao"], sistema.input["brilho"] = s, v
sistema.compute()
tabela = sistema.output["cabra"]  # tabela[s, v] = grau de 0 a 100

imagem, hsv = carregar_hsv()
grau = tabela[hsv[:, :, 1], hsv[:, :, 2]]
mascara = np.where(grau >= 55, 255, 0).astype(np.uint8)  # decisão final (corte-alfa)

# Esquerda: mapa de graus (preto = 0, branco = 100). Direita: região detectada.
salvar("resultado_fuzzy.png", imagem, limpar(mascara), (grau * 2.55).astype(np.uint8))
