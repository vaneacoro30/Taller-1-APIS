"""Lógica de dominio: evaluación de riesgo de pólizas."""
import csv
from pathlib import Path

import config
from utilidades import con_registro

BASE = Path(__file__).parent


class RepositorioHistorial:
    """Guarda las evaluaciones hechas por cualquier EvaluadorRiesgo.

    Vive fuera de EvaluadorRiesgo a propósito: el historial visible por
    GET /historial es un registro de la aplicación, no de una póliza en
    particular, así que es el colaborador opcional que sugiere el enunciado,
    no un atributo de la clase de dominio.
    """

    def __init__(self):
        self._registros = []

    def guardar(self, poliza, puntaje):
        self._registros.append({"poliza": poliza, "puntaje": puntaje})

    def todos(self):
        return list(self._registros)


class EvaluadorRiesgo:
    """Evalúa el riesgo de una póliza y guarda lo que ha evaluado."""

    umbral = config.UMBRAL_ALTO_RIESGO

    def __init__(self, poliza, repositorio=None):
        self.poliza = poliza
        self.historial = []
        self.repositorio = repositorio

    @con_registro
    def puntuar(self, modelo, payload):
        rasgos = [[
            payload["monto"],
            payload["antiguedad"],
            payload["siniestros_previos"],
        ]]
        return float(modelo.predict_proba(rasgos)[0][1])

    def anotar(self, puntaje):
        self.historial.append({"poliza": self.poliza, "puntaje": puntaje})
        if self.repositorio is not None:
            self.repositorio.guardar(self.poliza, puntaje)

    def es_alto_riesgo(self, puntaje):
        return puntaje is not None and puntaje > self.umbral


def cargar_siniestros():
    with open(BASE / config.RUTA_DATOS, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def buscar_siniestro(id_siniestro):
    for fila in cargar_siniestros():
        if fila["id"] == str(id_siniestro):
            return fila
    return None
