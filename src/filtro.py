"""Abordagem booleana: cada pixel é 'cabra' (1) ou 'não cabra' (0) por limites rígidos em HSV."""
import cv2
from core import carregar_hsv, limpar, salvar

imagem, hsv = carregar_hsv()

# saturação <= 70 e brilho >= 110 -> cabra
mascara = cv2.inRange(hsv, (0, 0, 110), (180, 70, 255))
salvar("resultado_filtro.png", imagem, limpar(mascara))
