"""
Esquemas de validación (entradas y salidas) del servicio.

Todas las entradas y salidas del contrato HTTP se declaran aquí con Pydantic
(`BaseModel`), con las restricciones expresadas en `Field` y al menos un
validador de campo. Así una entrada inválida la rechaza Pydantic y FastAPI
responde 422, en vez de romper el handler con un AssertionError o un KeyError.
"""
from pydantic import BaseModel, Field, field_validator


class SolicitudPuntuacion(BaseModel):
    """Datos de entrada de POST /score."""

    poliza: str = Field(min_length=1, description="Identificador de la póliza, p. ej. POL-2026-0413")
    monto: float = Field(gt=0, description="Monto declarado del siniestro; debe ser positivo")
    antiguedad: int = Field(ge=0, le=60, description="Años de antigüedad de la póliza")
    siniestros_previos: int = Field(ge=0, description="Número de siniestros previos declarados")

    @field_validator("poliza")
    @classmethod
    def normalizar_poliza(cls, v: str) -> str:
        """Quita espacios y exige el prefijo 'POL-' del dominio de la aseguradora."""
        v = v.strip().upper()
        if not v.startswith("POL-"):
            raise ValueError("la póliza debe empezar por 'POL-'")
        return v


class RespuestaPuntuacion(BaseModel):
    """Cuerpo de la respuesta de POST /score."""

    poliza: str
    puntaje: float = Field(ge=0.0, le=1.0)
    alto_riesgo: bool


class Siniestro(BaseModel):
    """Una fila del archivo de siniestros (salida de /siniestros/{id} y /exportar)."""

    id: int
    poliza: str
    monto: float
    antiguedad: int
    siniestros_previos: int
    pago_alto: int
