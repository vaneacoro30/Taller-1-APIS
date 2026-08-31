"""
Cálculo intensivo en CPU, aislado en su propio módulo.

Vive fuera de `main.py` a propósito: el `ProcessPoolExecutor` de
`/calculo-pesado` arranca procesos hijos que, en Windows, reimportan el módulo
donde está la función. Al tenerla aquí, esos hijos importan solo esto —una
función de aritmética pura— y no vuelven a cargar el modelo ni levantar la app.
"""


def reserva_agregada(iteraciones: int = 3_000_000) -> float:
    """Recalcula la reserva agregada. Trabajo puramente CPU-bound."""
    total = 0.0
    for i in range(iteraciones):
        total += (i % 7) ** 0.5
    return round(total, 2)
