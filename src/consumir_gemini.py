import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

MODELO = "gemini-3.5-flash"


def armar_peticion(pregunta):
    if not pregunta or not pregunta.strip():
        raise ValueError("La pregunta no puede estar vacía.")
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Falta la variable GEMINI_API_KEY en el archivo .env de la raíz del proyecto.")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODELO}:generateContent"
    body = {"contents": [{"parts": [{"text": pregunta}]}]}
    headers = {"x-goog-api-key": api_key}
    return url, body, headers


def enviar_peticion(url, body, headers):
    try:
        respuesta = requests.post(url, json=body, headers=headers, timeout=30)
    except requests.exceptions.ConnectionError:
        raise RuntimeError("No se pudo conectar con el servicio. Revisa tu conexión e intenta de nuevo en unos segundos.")
    except requests.exceptions.Timeout:
        raise RuntimeError("El servicio no respondió dentro de 30 segundos.")
    try:
        return respuesta.json()
    except requests.exceptions.JSONDecodeError:
        raise RuntimeError(f"La respuesta del servicio no llegó en formato JSON (código HTTP {respuesta.status_code}).")


def extraer_texto(datos):
    if "error" in datos:
        detalle = datos["error"].get("message", "sin detalle")
        raise RuntimeError(f"El servicio rechazó la petición: {detalle}")
    try:
        return datos["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise RuntimeError("La respuesta no trae el texto generado en candidates[0].content.parts[0].text.")


def obtener_dato_de_prueba(pregunta):
    url, body, headers = armar_peticion(pregunta)
    datos = enviar_peticion(url, body, headers)
    return extraer_texto(datos)


if __name__ == "__main__":
    pregunta = sys.argv[1] if len(sys.argv) > 1 else "Confirma en una frase corta que esta conexión funciona"
    try:
        resultado = obtener_dato_de_prueba(pregunta)
        print(resultado)
    except (ValueError, RuntimeError) as error:
        print("No se pudo completar la operación:", error)
