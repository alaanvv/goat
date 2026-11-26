"""Abordagem fuzzy (Mamdani): o grau de 'parecer cabra' vem de regras sobre saturação e brilho."""
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from core import carregar_hsv, limpar, salvar

# Variáveis linguísticas e fuzzificação
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

# Regras
regras = [
    ctrl.Rule(saturacao["baixa"] & brilho["claro"], cabra["sim"]),
    ctrl.Rule(saturacao["baixa"] & brilho["medio"], cabra["sim"]),
    ctrl.Rule(saturacao["baixa"] & brilho["escuro"], cabra["talvez"]),
    ctrl.Rule(saturacao["media"] & ~brilho["escuro"], cabra["talvez"]),
    ctrl.Rule(saturacao["alta"], cabra["nao"]),
    ctrl.Rule(brilho["escuro"] & ~saturacao["baixa"], cabra["nao"]),
]
sistema = ctrl.ControlSystemSimulation(ctrl.ControlSystem(regras))

# Defuzzificação
s, v = np.meshgrid(universo, universo, indexing="ij")
sistema.input["saturacao"], sistema.input["brilho"] = s, v
sistema.compute()
tabela = sistema.output["cabra"]

imagem, hsv = carregar_hsv()
grau = tabela[hsv[:, :, 1], hsv[:, :, 2]]
mascara = np.where(grau >= 55, 255, 0).astype(np.uint8)

# Esquerda: mapa de graus; Direita: região detectada
salvar("resultado_fuzzy.png", imagem, limpar(mascara), (grau * 2.55).astype(np.uint8))
