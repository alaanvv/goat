"""Funções compartilhadas: carregar a imagem, limpar a máscara e salvar o resultado."""
from pathlib import Path
import cv2
import numpy as np

PASTA = Path(__file__).parent


def carregar_hsv():
    imagem = cv2.imread(str(PASTA / "cabra.jpg"))
    if imagem is None:
        raise SystemExit("Não foi possível abrir cabra.jpg")
    return imagem, cv2.cvtColor(imagem, cv2.COLOR_BGR2HSV)


def limpar(mascara):
    """Remove ruído, descarta regiões pequenas (< 1% da imagem) e preenche os buracos."""
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_OPEN, kernel)
    mascara = cv2.morphologyEx(mascara, cv2.MORPH_CLOSE, kernel, iterations=2)
    _, rotulos, stats, _ = cv2.connectedComponentsWithStats(mascara)
    grandes = np.flatnonzero(stats[:, cv2.CC_STAT_AREA] >= 0.01 * mascara.size)
    grandes = grandes[grandes != 0]  # rótulo 0 é o fundo
    mascara = np.where(np.isin(rotulos, grandes), 255, 0).astype(np.uint8)
    contornos, _ = cv2.findContours(mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return cv2.drawContours(mascara, contornos, -1, 255, cv2.FILLED)


def salvar(nome, imagem, mascara, extra=None):
    """Pinta a região detectada de verde (semitransparente) e salva lado a lado com `extra`."""
    verde = imagem.copy()
    verde[mascara > 0] = (0, 255, 0)
    resultado = cv2.addWeighted(imagem, 0.5, verde, 0.5, 0)
    if extra is not None:
        resultado = np.hstack([cv2.cvtColor(extra, cv2.COLOR_GRAY2BGR), resultado])
    cv2.imwrite(str(PASTA / nome), resultado)
    print(f"Salvo: {nome}  ({100 * np.count_nonzero(mascara) / mascara.size:.1f}% da imagem)")
