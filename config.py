"""Configuración del servicio."""
import os

from dotenv import load_dotenv

load_dotenv()

# os.getenv (no os.environ[...]) para que el servicio arranque en una máquina
# limpia sin .env: ninguna línea del código usa estas dos variables todavía,
# así que exigirlas con KeyError tumbaba el arranque por un valor que nadie lee.
API_KEY = os.getenv("API_KEY")
CLAVE_FIRMA = os.getenv("CLAVE_FIRMA")

UMBRAL_ALTO_RIESGO = 0.7
RUTA_MODELO = "modelo.pkl"
RUTA_DATOS = "datos/siniestros.csv"
