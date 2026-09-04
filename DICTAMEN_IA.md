# Dictamen sobre `ia_propuesta.py` — Parte D

**Integrantes:** Vanessa Acosta, Mateo Ramos

> Tres defectos. Las cuatro secciones de cada uno son obligatorias y se parsean.
> El peso está en **«Cómo lo comprobamos»**: afirmar que algo está mal no vale;
> demostrarlo, sí.

## Defecto 1

- **Qué está mal:** El validador `redondear_monto` (`@field_validator("monto")`) calcula `round(v, 2)` pero no hace `return`. En Pydantic v2, el valor que devuelve un `field_validator` **reemplaza** el valor del campo; una función sin `return` devuelve `None` implícitamente, así que **cualquier `monto` válido queda en `None`** después de validar.
- **Por qué es un defecto** (módulo · sección): M4 · 6. Validadores de campo — el material muestra el patrón correcto de un `field_validator`: transformar el dato y **siempre `return` el valor** (`return v.lower()`, `return float(v.replace(',', '.'))`, etc.). Omitir el `return` rompe ese contrato silenciosamente: no lanza ningún error, simplemente borra el dato.

- **Cómo lo comprobamos:**

```python
from ia_propuesta import SolicitudPuntuacion
s = SolicitudPuntuacion(poliza='POL-2026-0413', correo_analista='ana@usta.edu',
                         monto=4200000, antiguedad=3, siniestros_previos=1)
print('s.monto:', s.monto)
```

```
s.monto: None
```

- **Corrección:** Agregar `return round(v, 2)` al final del validador (ver `ia_propuesta_corregida.py`). Verificado: con la misma llamada, `s.monto` da `4200000.46` (con `monto=4200000.456`), no `None`.

## Defecto 2

- **Qué está mal:** `_puntuar` es una función `async def` pero espera con `time.sleep(0.2)`, una llamada **bloqueante**. `time.sleep` no cede el control del event loop, así que cuando `evaluar_lote` llama a `asyncio.gather(*[_puntuar(s) for s in solicitudes])`, las corrutinas no se solapan: cada `time.sleep` bloquea a las demás y el lote se procesa **secuencial**, no concurrente — exactamente lo que el prompt original pedía evitar ("evalúe un lote... concurrentemente").
- **Por qué es un defecto** (módulo · sección): M5 · 6. Síncrono frente a asíncrono — el material compara ambas versiones lado a lado: `time.sleep(0.3)` (bloquea) frente a `await asyncio.sleep(0.3)` (**"NO bloquea, cede control"**). `_puntuar` usa la forma que el material marca como la que hay que evitar dentro de una corrutina.

- **Cómo lo comprobamos:**

```python
import asyncio, time
from ia_propuesta import evaluar_lote

class Solicitud:
    def __init__(self, siniestros_previos, antiguedad):
        self.siniestros_previos = siniestros_previos
        self.antiguedad = antiguedad

solicitudes = [Solicitud(1, 3) for _ in range(5)]
t0 = time.perf_counter()
asyncio.run(evaluar_lote(solicitudes))
print(f'tiempo total: {time.perf_counter() - t0:.2f}s')
```

```
tiempo total: 1.00s
```

- **Corrección:** Cambiar `time.sleep(0.2)` por `await asyncio.sleep(0.2)` (ver `ia_propuesta_corregida.py`). Verificado con el mismo script: el lote de 5 solicitudes pasó de **1.00s a 0.22s** — ahora sí corre concurrente (≈ el tiempo de una sola espera, no la suma de las cinco).

## Defecto 3

- **Qué está mal:** El patrón de `correo_analista` (`r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,3}$"`) solo permite **un** nivel de dominio después del `@` (`nombre@dominio.tld`). Rechaza direcciones institucionales legítimas con subdominios, como `analista@usta.edu.co`, que son exactamente el tipo de correo que un analista de una aseguradora universitaria usaría.
- **Por qué es un defecto** (módulo · sección): M4 · 4. El poder de Field — el material usa `Field(pattern=...)` con el mismo propósito (validar formato de correo, `r"^[\w\.-]+@[\w\.-]+\.\w+$"` en su ejemplo), pero con un patrón que sí admite múltiples segmentos de dominio (`[\w\.-]+` acepta puntos). El de `ia_propuesta.py` restringe el dominio a `[A-Za-z0-9-]+` (sin punto) seguido de un solo `.` — una regex más estricta de lo que el propio material recomienda.

- **Cómo lo comprobamos:**

```python
from ia_propuesta import SolicitudPuntuacion
from pydantic import ValidationError
try:
    s = SolicitudPuntuacion(poliza='POL-2026-0413', correo_analista='ana@usta.edu.co',
                             monto=4200000, antiguedad=3, siniestros_previos=1)
    print('paso la validacion:', s.correo_analista)
except ValidationError as e:
    print(e)
```

```
1 validation error for SolicitudPuntuacion
correo_analista
  String should match pattern '^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+\.[A-Za-z]{2,3}$' [type=string_pattern_mismatch, input_value='ana@usta.edu.co', input_type=str]
```

- **Corrección:** Ampliar el patrón a `r"^[A-Za-z0-9_.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$"`, que admite cero o más subdominios intermedios (ver `ia_propuesta_corregida.py`). Verificado: `ana@usta.edu.co` ya valida correctamente, y `gmail.com` y patrones de basura (`invalido`, `a@b`) se comportan igual que antes.
