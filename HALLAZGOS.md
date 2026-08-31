# Hallazgos — Parte A

**Grupo:** <número> · **Integrantes:** Vanessa Acosta, Mateo Ramos

> No borren la fila de ejemplo hasta haber comprobado que su tabla se parsea.
> El formato es rígido: siete columnas, en este orden. Una tabla torcida se
> rechaza indicando la línea, no se «entiende igual».
>
> **Tuberías dentro de una celda:** si su comando lleva `|` —y varios lo llevarán,
> por `grep`, `head` o `jq`— escríbanlo `\|`. Sin escapar, Markdown lo lee como
> separador de columna y su fila pasa a tener ocho.

| ID | Síntoma observable | Causa | Módulo · Sección | SHA donde se observa | Comando de evidencia | Salida obtenida | Corrección aplicada |
|----|--------------------|-------|------------------|----------------------|----------------------|-----------------|---------------------|
| H1 | *(ejemplo de FORMATO, no un defecto de este repositorio)* `GET /ping` responde sin cabecera `Cache-Control` | El handler no declara política de caché | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -sI localhost:8000/ping \| grep -ci cache-control` | `0` | Se añade la cabecera en la respuesta |
| H2 | `config.py` trae `API_KEY` y `CLAVE_FIRMA` escritos en texto plano y quedan versionados en git; el `.gitignore` solo excluye `*.pyc`, así que ni un `.env` con esas mismas claves quedaría protegido | Los secretos se dejaron hardcodeados en el módulo de configuración en lugar de leerse de variables de entorno, y el `.gitignore` nunca se amplió para excluir archivos de credenciales | M1 · 5. Git y GitHub para investigadores (Material de Clase) | `6a91db1` | `grep -n "API_KEY\|CLAVE_FIRMA" config.py` | `4:API_KEY = "sk-riesgo-2026-9f3a1c7b4e21"`<br>`5:CLAVE_FIRMA = "aseguradora-santo-tomas-2026"` | *(pendiente — se llena en la Parte B)* |
| H3 | *(pendiente Vanessa — decorador sin `functools.wraps` en `utilidades.py`, B9)* | | | | | | |
| H4 | *(pendiente Vanessa — el decorador `con_registro` captura toda excepción y devuelve `None` en silencio, B9)* | | | | | | |
| H5 | *(pendiente Vanessa — `historial` es atributo de clase en `EvaluadorRiesgo`, compartido entre instancias, B4)* | | | | | | |
| H6 | *(pendiente Vanessa — `requirements.txt` sin versiones fijadas, B1)* | | | | | | |
| H7 | `README.md` documenta `uvicorn main:app --reload --host 0.0.0.0 --port 8000` como el comando "que sirve en el servidor de producción", y `main.py` arranca el servicio con `reload=True` | No se distingue el servidor de desarrollo (recarga en caliente) del arranque de producción; falta `--workers` | M5 · 3. El servidor web y WSGI | `6a91db1` | `cat README.md main.py \| grep -Ec -- "--reload\|reload=True"` | `3` | Arranque documentado sin `--reload` y con `--workers` (`uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`); se elimina el `reload=True` de `main.py` |
| H8 | `GET /exportar` responde con `content-type: application/octet-stream` (pickle), no JSON | El handler serializa la respuesta con `pickle.dumps` en vez de devolver algo serializable a JSON | M2 · 3. JSON frente a Pickle | `6a91db1` | `curl -s -D - localhost:8000/exportar -o /dev/null \| grep -i content-type` | `content-type: application/octet-stream` | Se reemplaza `Response(pickle.dumps(datos), ...)` por una respuesta JSON (`response_model=list[Siniestro]`) |
| H9 | `POST /score` con `monto` negativo responde `500`, no `422` | La validación usa `assert payload["monto"] > 0`, que lanza `AssertionError` no controlada en vez de una validación declarativa | M4 · 6. Validadores de campo | `6a91db1` | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"poliza":"POL-2026-0413","monto":-5,"antiguedad":3,"siniestros_previos":1}'` | `500` | `monto` se declara en un `BaseModel` con `Field(gt=0)`; Pydantic devuelve `422` automáticamente |
| H10 | `POST /score` sin el campo `poliza` responde `200` con `{"error": "falta el campo poliza"}` en el cuerpo | La validación es manual con `if`/`return`; el error de negocio no se traduce a un código de estado, viaja en el cuerpo con `200` | M2 · 2. El protocolo HTTP y la autenticación | `6a91db1` | `curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"monto":1000,"antiguedad":3,"siniestros_previos":1}'` | `{"error":"falta el campo poliza"}`<br>`HTTP_STATUS:200` | Entrada validada con `BaseModel`; campo faltante → `422` automático vía `ValidationError`, nunca `200` |
| H11 | `modelo.pkl` se abre y deserializa dentro del handler `async def score`, en cada petición | No hay carga del modelo al iniciar el servicio; `pickle.load` vive dentro del handler | M5 · 8. Resumen y mejores prácticas | `6a91db1` | `grep -n "pickle.load" main.py` | `29:        modelo = pickle.load(fh)` | El modelo se carga una sola vez al iniciar el servicio (en la constante de módulo `MODELO`, al importar `main`) y se reutiliza en cada petición; ya no se abre `pickle` dentro del handler |
| H12 | `GET /health` responde `404` | El endpoint no existe en `main.py` | M5 · 8. Resumen y mejores prácticas | `6a91db1` | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/health` | `404` | Se añade `GET /health` que responde `200` |


**Reglas que se verifican automáticamente:**

- `Módulo · Sección` debe citar una lección que exista en los módulos 1 a 5, con el
  título tal como aparece en el menú lateral del material.
- **`SHA donde se observa`** es el commit donde el defecto todavía está: normalmente
  `v0-semilla`, la etiqueta del repositorio tal como se lo entregamos. El calificador hace
  *checkout* de ese commit para reproducir la evidencia. Si lo dejan en el commit final —donde
  ya está corregido— el comando no reproducirá nada y la fila no cuenta.
- `Comando de evidencia` se ejecuta ahí. Escríbanlo contra `localhost:8000`; el calificador
  sustituye el puerto por el que use.
- `Salida obtenida` es literal, copiada de su terminal. **Se compara con lo que salga de
  verdad**, así que una salida inventada se detecta.
- Entre 6 y 12 hallazgos. Una fila que no corresponda a un defecto real resta la mitad de lo
  que suma una correcta: el máximo se alcanza con precisión, no con volumen.

---

# Parte C — Interpretación de las mediciones

> Un párrafo por endpoint. Expliquen **los tiempos que ustedes obtuvieron**, no la
> teoría general. Si un resultado los sorprendió, dígan­lo: eso se premia.

**Nota de método.** Todas las mediciones se tomaron con **un solo worker** de
uvicorn (`--workers 1`). Es deliberado: con varios workers el sistema operativo
reparte las peticiones entre procesos y **oculta** el efecto de cómo está
declarado el handler, que es justo lo que esta parte evalúa. Con un worker se ve
si el handler bloquea o no el event loop. No se modificó `medir.py`. Los números
del estado semilla (antes de corregir) están en `MEDICIONES_semilla.csv`; los del
estado corregido, en `MEDICIONES.csv`. Máquina: 4 núcleos lógicos.

## `/ping`

Clasificación **trivial**, decisión **`async def`**. Devuelve una constante sin
tocar disco, red ni CPU, así que nunca bloquea el event loop: `async def` es
adecuado y evita el salto al threadpool que impondría `def`. Medido: p50 de
**1.2 ms** a concurrencia 1 y **1.8 ms** a concurrencia 20 — instantáneo en ambos
casos. El `tiempo_total` (2.07 s) y el p95 (~2.06 s) a concurrencia 20 no vienen
del handler sino de abrir 20 conexiones TCP nuevas de golpe contra `localhost`;
el p50 de 1.8 ms lo confirma: la enorme mayoría responde al instante y solo un par
de conexiones nuevas pagan ese arranque. Mismo patrón aparece en `/consulta-archivo`,
lo que reafirma que es un costo del cliente, no del endpoint.

## `/consulta-archivo`

Clasificación **IO-bound**, decisión **`def`**. Lee un archivo con
`open()`/`read_text`, que es I/O **síncrona**; declararlo `def` hace que FastAPI lo
ejecute en su threadpool y no bloquee el event loop (no cabe `await`, porque
`read_text` no es asíncrono). Aquí está la sorpresa que solo se ve midiendo: pasar
el handler de `async def` (semilla) a `def` **no cambió los números** — p50 de
**2.2 ms** (async, semilla) frente a **2.3 ms** (`def`) a concurrencia 20, dentro
del ruido. El archivo son 400 filas (~13 KB): leerlo tarda microsegundos, así que
bloquear o no el loop durante ese instante es irrelevante. La clasificación dice
"es I/O, cuida el bloqueo", pero la medición dice que **en este caso da
exactamente igual**. La decisión `def` se justifica por principio (sería lo
correcto si el archivo creciera), no por los números de hoy.

## `/servicio-externo`

Clasificación **IO-bound**, decisión **`async def`** (con `await asyncio.sleep`).
La regla "I/O va con async" es correcta aquí, pero **solo si se espera de verdad
sin bloquear**. La versión semilla era `async def` + `time.sleep(0.3)`: parecía
async pero `time.sleep` bloquea el event loop, y la medición lo delata — a
concurrencia 20 tardaba **15.15 s** (igual que a concurrencia 1) con p95 de
**14.4 s**. Al cambiar `time.sleep` por `await asyncio.sleep`, el loop cede el
control durante la espera y atiende las 20 en paralelo: el `tiempo_total` a
concurrencia 20 cayó de **15.15 s a 2.99 s**. A concurrencia 1 no hay diferencia
(15.65 s ≈ 50 × 0.3 s): sin concurrencia no hay nada que solapar. Es la trampa
"seguir la regla da peor": poner `async def` sin `await` real no escala; hay que
awaitar (o, con un cliente síncrono, usar `def` para el threadpool).

## `/calculo-pesado`

Clasificación **CPU-bound**, decisión **`async def + executor`**
(`ProcessPoolExecutor` de 4 procesos). El cálculo (3M iteraciones, ~0.3 s) es puro
CPU. En `async def` puro (semilla) bloquea el event loop: a concurrencia 20
tardaba **13.66 s**, igual que a concurrencia 1, con p95 de **13 s**. Un threadpool
(`def`) tampoco ayudaría: el GIL serializa el cómputo entre hilos. Descargándolo a
un `ProcessPoolExecutor`, cada proceso corre en su núcleo y el `tiempo_total` a
concurrencia 20 bajó de **13.66 s a 9.64 s**, y el p95 de 13 s a **5.3 s**. La
mejora es real pero **no 4×**: la máquina tiene 4 núcleos lógicos (≈2 físicos con
hyperthreading, que el trabajo CPU aprovecha poco) y el pool paga el costo de
serializar tarea y resultado entre procesos. Ese costo se ve claro a concurrencia
1, donde el pool va **peor** que la semilla (15.77 s frente a 13.55 s): sin
concurrencia que explotar, mover el trabajo a otro proceso es solo overhead. El
executor paga cuando hay peticiones simultáneas, no antes.
