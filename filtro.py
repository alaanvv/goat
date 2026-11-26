"""Abordagem booleana: cada pixel é 'cabra' (1) ou 'não cabra' (0) por limites rígidos em HSV."""
import cv2
from comum import carregar_hsv, limpar, salvar

imagem, hsv = carregar_hsv()

# Regra rígida: SE saturação <= 70 E brilho >= 110 ENTÃO cabra.
# Um pixel com saturação 71 ou brilho 109 é descartado por inteiro.
mascara = cv2.inRange(hsv, (0, 0, 110), (180, 70, 255))
salvar("resultado_filtro.png", imagem, limpar(mascara))
