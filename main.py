"""
riesgo-api-v0 — Servicio de puntuación de siniestros.
Aseguradora Santo Tomás · prototipo interno.
"""
import pickle
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException

import config
from dominio import EvaluadorRiesgo, buscar_siniestro, cargar_siniestros
from esquemas import RespuestaPuntuacion, Siniestro, SolicitudPuntuacion

BASE = Path(__file__).parent
app = FastAPI(title="Riesgo API", version="0.1.0")


def cargar_modelo():
    """Carga el modelo serializado una sola vez, al iniciar el servicio."""
    with open(BASE / config.RUTA_MODELO, "rb") as fh:
        return pickle.load(fh)


# El modelo se carga al importar el módulo (arranque del servicio), no dentro
# del handler: así se deserializa una vez por proceso y no en cada petición.
MODELO = cargar_modelo()


@app.post("/score", response_model=RespuestaPuntuacion)
async def score(solicitud: SolicitudPuntuacion):
    evaluador = EvaluadorRiesgo(solicitud.poliza)
    puntaje = evaluador.puntuar(MODELO, solicitud.model_dump())
    evaluador.anotar(puntaje)
    return RespuestaPuntuacion(
        poliza=solicitud.poliza,
        puntaje=puntaje,
        alto_riesgo=evaluador.es_alto_riesgo(puntaje),
    )


@app.get("/historial")
async def historial():
    return {"evaluaciones": EvaluadorRiesgo.historial}


@app.get("/siniestros/{id_siniestro}", response_model=Siniestro)
async def siniestro(id_siniestro: int):
    fila = buscar_siniestro(id_siniestro)
    if fila is None:
        raise HTTPException(status_code=404, detail=f"no existe el siniestro {id_siniestro}")
    return fila


@app.get("/exportar", response_model=list[Siniestro])
async def exportar():
    return cargar_siniestros()


@app.get("/health")
async def health():
    return {"status": "ok"}


# --- Endpoints de perfil de carga -----------------------------------------

@app.get("/ping")
async def ping():
    return {"pong": True}


@app.get("/consulta-archivo")
async def consulta_archivo():
    contenido = (BASE / config.RUTA_DATOS).read_text(encoding="utf-8")
    return {"lineas": len(contenido.splitlines())}


@app.get("/servicio-externo")
async def servicio_externo():
    time.sleep(0.3)
    return {"tarifa_referencia": 1.18}


@app.get("/calculo-pesado")
async def calculo_pesado():
    total = 0.0
    for i in range(3_000_000):
        total += (i % 7) ** 0.5
    return {"total": round(total, 2)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
