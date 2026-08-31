"""
Propuesta generada por un asistente de IA para riesgo-api-v0, corregida.

Prompt original:
    «Escribe con Pydantic v2 los modelos de validación de una solicitud de
     puntuación de siniestros, y una función asíncrona que evalúe un lote de
     solicitudes concurrentemente. Aplica buenas prácticas.»

Tres correcciones respecto a `ia_propuesta.py` — ver DICTAMEN_IA.md para el
"qué está mal" y "cómo lo comprobamos" de cada una:

1. `redondear_monto` ahora hace `return`. Sin él, Pydantic v2 sustituye el
   campo por lo que devuelva el validador, y una función sin `return` devuelve
   `None`: cualquier `monto` válido quedaba en `None` tras validar.
2. `_puntuar` espera con `await asyncio.sleep` en vez de `time.sleep`. El
   original bloqueaba el hilo del event loop, así que `asyncio.gather`
   procesaba el lote secuencial, no concurrente.
3. El patrón de `correo_analista` admite dominios de varios niveles
   (`usta.edu.co`), no solo `dominio.tld`.
"""
import asyncio
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SolicitudPuntuacion(BaseModel):
    """Datos de entrada para puntuar una póliza."""

    poliza: str = Field(min_length=8, max_length=20)
    correo_analista: str = Field(
        pattern=r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"
    )
    monto: float = Field(gt=0)
    antiguedad: int = Field(ge=0, le=60)
    siniestros_previos: int = Field(ge=0)
    observaciones: Optional[str] = Field(default=None, max_length=200)

    @field_validator("monto")
    @classmethod
    def redondear_monto(cls, v: float) -> float:
        """Redondea el monto a dos decimales para evitar ruido de coma flotante."""
        return round(v, 2)


class RespuestaPuntuacion(BaseModel):
    """Resultado de la evaluación."""

    poliza: str
    puntaje: float = Field(ge=0.0, le=1.0)
    alto_riesgo: bool


async def _puntuar(solicitud: SolicitudPuntuacion) -> float:
    """Consulta el servicio externo de scoring y devuelve la probabilidad."""
    await asyncio.sleep(0.2)  # latencia típica del servicio de scoring
    base = 0.18 * solicitud.siniestros_previos - 0.01 * solicitud.antiguedad
    return max(0.0, min(1.0, 0.4 + base))


async def evaluar_lote(solicitudes) -> list:
    """Evalúa un lote de solicitudes de forma concurrente."""
    return await asyncio.gather(*[_puntuar(s) for s in solicitudes])
