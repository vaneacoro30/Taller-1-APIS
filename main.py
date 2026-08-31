"""
riesgo-api-v0 — Servicio de puntuación de siniestros.
Aseguradora Santo Tomás · prototipo interno.
"""
import asyncio
import pickle
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from fastapi import FastAPI, HTTPException

import computo
import config
from dominio import EvaluadorRiesgo, buscar_siniestro, cargar_siniestros
from esquemas import RespuestaPuntuacion, Siniestro, SolicitudPuntuacion

BASE = Path(__file__).parent
app = FastAPI(title="Riesgo API", version="0.1.0")

# Pool de procesos para el trabajo CPU-bound de /calculo-pesado. Se crea de
# forma perezosa en la primera petición (no al importar) para que los procesos
# hijos que arranca no vuelvan a ejecutar este módulo en cascada en Windows.
_pool_cpu = None


def _pool() -> ProcessPoolExecutor:
    global _pool_cpu
    if _pool_cpu is None:
        _pool_cpu = ProcessPoolExecutor(max_workers=4)
    return _pool_cpu


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
def consulta_archivo():
    # IO-bound con lectura de archivo síncrona (open/read_text). Se declara con
    # `def` para que FastAPI lo ejecute en su threadpool y no bloquee el event
    # loop; `await` no aplica porque `read_text` no es asíncrono.
    contenido = (BASE / config.RUTA_DATOS).read_text(encoding="utf-8")
    return {"lineas": len(contenido.splitlines())}


@app.get("/servicio-externo")
async def servicio_externo():
    # IO-bound (espera de red simulada). Se usa `await asyncio.sleep`, que cede
    # el control del event loop mientras espera, en vez de `time.sleep`, que lo
    # bloquea. En producción, la llamada real iría con httpx.AsyncClient.
    await asyncio.sleep(0.3)
    return {"tarifa_referencia": 1.18}


@app.get("/calculo-pesado")
async def calculo_pesado():
    # CPU-bound: se descarga en un ProcessPoolExecutor con run_in_executor para
    # aprovechar varios núcleos y no bloquear el event loop. Un threadpool (def)
    # no bastaría: el GIL serializa el cálculo entre hilos.
    loop = asyncio.get_running_loop()
    total = await loop.run_in_executor(_pool(), computo.reserva_agregada)
    return {"total": total}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
