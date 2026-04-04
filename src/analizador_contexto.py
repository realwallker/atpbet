from textblob import TextBlob

def analizar_sentimiento_noticia(titular_en_ingles):
    """
    Analiza un titular y devuelve un ajuste de probabilidad.
    Input: "Nadal suffering from knee pain" -> Output: -0.05
    """
    analisis = TextBlob(titular_en_ingles)
    polaridad = analisis.sentiment.polarity # Va de -1 a 1
    
    # Mapeamos la polaridad de -1/1 a un ajuste de -0.05/+0.05
    ajuste = polaridad * 0.05
    
    return ajuste


    # Añade esto a tu src/analizador_contexto.py
import requests

def buscar_noticias_recientes(nombre_jugador):
    # Usaremos una URL de búsqueda simple para simular la obtención de titulares
    # En una fase avanzada usaremos NewsAPI o un scraper de X (Twitter)
    return [f"{nombre_jugador} is in great form", f"{nombre_jugador} training hard"]



# Ejemplo de uso interno:
# noticia = "Djokovic confirms he is in peak physical condition"
# print(analizar_sentimiento_noticia(noticia))