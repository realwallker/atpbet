import pickle
import pandas as pd
import numpy as np

def detectar_valor(cuota_casa, prob_modelo):
    # Probabilidad implícita de la casa
    prob_casa = 1 / cuota_casa
    
    # Si nuestra probabilidad es mayor a la de la casa, hay VALOR
    if prob_modelo > prob_casa:
        valor = (prob_modelo * cuota_casa) - 1
        return valor
    return 0

# (Este script se expandirá cuando conectemos la API de partidos de hoy)