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
| H2 | `README.md` documenta `uvicorn main:app --reload --host 0.0.0.0 --port 8000` como el comando "que sirve en el servidor de producción", y `main.py` arranca el servicio con `reload=True` | No se distingue el servidor de desarrollo (recarga en caliente) del arranque de producción; falta `--workers` | M5 · 3. El servidor web y WSGI | `v0-semilla` | `cat README.md main.py \| grep -Ec -- "--reload\|reload=True"` | `3` | Arranque documentado sin `--reload` y con `--workers` (`uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`); se elimina el `reload=True` de `main.py` |
| H3 | `GET /exportar` responde con `content-type: application/octet-stream` (pickle), no JSON | El handler serializa la respuesta con `pickle.dumps` en vez de devolver algo serializable a JSON | M2 · 3. JSON frente a Pickle | `v0-semilla` | `curl -s -D - localhost:8000/exportar -o /dev/null \| grep -i content-type` | `content-type: application/octet-stream` | Se reemplaza `Response(pickle.dumps(datos), ...)` por una respuesta JSON |
| H4 | `POST /score` con `monto` negativo responde `500`, no `422` | La validación usa `assert payload["monto"] > 0`, que lanza `AssertionError` no controlada en vez de una validación declarativa | M4 · 6. Validadores de campo | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"poliza":"POL-2026-0413","monto":-5,"antiguedad":3,"siniestros_previos":1}'` | `500` | `monto` se declara en un `BaseModel` con `Field(gt=0)`; Pydantic devuelve `422` automáticamente |
| H5 | `POST /score` sin el campo `poliza` responde `200` con `{"error": "falta el campo poliza"}` en el cuerpo | La validación es manual con `if`/`return`; el error de negocio no se traduce a un código de estado, viaja en el cuerpo con `200` | M2 · 2. El protocolo HTTP y la autenticación | `v0-semilla` | `curl -s -w "\nHTTP_STATUS:%{http_code}\n" -X POST localhost:8000/score -H "Content-Type: application/json" -d '{"monto":1000,"antiguedad":3,"siniestros_previos":1}'` | `{"error":"falta el campo poliza"}`<br>`HTTP_STATUS:200` | Entrada validada con `BaseModel`; campo faltante → `422` automático vía `ValidationError`, nunca `200` |
| H6 | `modelo.pkl` se abre y deserializa dentro del handler `async def score`, en cada petición | No hay carga del modelo en un evento de arranque (`startup`/`lifespan`); `pickle.load` vive dentro del handler | M5 · 8. Resumen y mejores prácticas | `v0-semilla` | `grep -n "pickle.load" main.py` | `29:        modelo = pickle.load(fh)` | El modelo se carga una sola vez en un evento `lifespan` y se reutiliza desde el estado de la app, no dentro del handler |
| H7 | `GET /health` responde `404` | El endpoint no existe en `main.py` | M5 · 8. Resumen y mejores prácticas | `v0-semilla` | `curl -s -o /dev/null -w "%{http_code}" localhost:8000/health` | `404` | Se añade `GET /health` que responde `200` |


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

## `/ping`

## `/consulta-archivo`

## `/servicio-externo`

## `/calculo-pesado`
