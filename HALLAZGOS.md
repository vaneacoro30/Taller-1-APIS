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
| H8 | `config.py` trae `API_KEY` y `CLAVE_FIRMA` escritos en texto plano y quedan versionados en git; el `.gitignore` solo excluye `*.pyc`, así que ni un `.env` con esas mismas claves quedaría protegido | Los secretos se dejaron hardcodeados en el módulo de configuración en lugar de leerse de variables de entorno, y el `.gitignore` nunca se amplió para excluir archivos de credenciales | M1 · 5. Git y GitHub para investigadores (Material de Clase) | `6a91db1` | `grep -n "API_KEY\|CLAVE_FIRMA" config.py` | `4:API_KEY = "sk-riesgo-2026-9f3a1c7b4e21"`<br>`5:CLAVE_FIRMA = "aseguradora-santo-tomas-2026"` | *(pendiente — se llena en la Parte B)* |
| H9 | `EvaluadorRiesgo.puntuar.__name__` devuelve `envoltura` en vez de `puntuar`: el decorador `@con_registro` oculta la identidad real del método que envuelve | `con_registro` define la función interna `envoltura` sin aplicar `functools.wraps(func)`, así que Python nunca copia `__name__`, `__doc__` ni `__module__` de la función original a la envoltura | M1 · 6. Decoradores como guardianes (Material de Clase) | `6a91db1` | `py -c "from dominio import EvaluadorRiesgo; print(EvaluadorRiesgo.puntuar.__name__)"` | `envoltura` | *(pendiente — se llena en la Parte B)* |
| H10 | Al forzar un error dentro de `puntuar` (payload sin la clave `monto`), la llamada no lanza excepción: imprime un log y devuelve `None`. Quien use `EvaluadorRiesgo.puntuar` no puede distinguir "sin riesgo" de "falló silenciosamente" | `con_registro` usa un `except Exception` genérico que atrapa cualquier error, lo registra con `print` y siempre retorna `None`, sin volver a lanzar (`raise`) ni distinguir el tipo de excepción | M1 · 6. Decoradores como guardianes (Material de Clase) | `6a91db1` | `py -c "from dominio import EvaluadorRiesgo; r = EvaluadorRiesgo('POL-1').puntuar(None, {}); print('resultado:', r)"` | `[registro] puntuar falló: 'monto'`<br>`resultado: None` | *(pendiente — se llena en la Parte B)* |
| H11 | Dos pólizas distintas (`EvaluadorRiesgo('POL-1')` y `EvaluadorRiesgo('POL-2')`), cada una anotando su propio puntaje, terminan compartiendo el mismo `historial`: el de `POL-1` incluye también la entrada de `POL-2`, y viceversa | `historial = []` se declara a nivel de clase (fuera de `__init__`), así que es un único objeto lista compartido por todas las instancias; `anotar` lo muta con `.append()` en vez de operar sobre un `historial` propio de cada objeto | M3 · 3. Componentes: atributos de clase (Material de Clase) | `6a91db1` | `py -c "from dominio import EvaluadorRiesgo; e1=EvaluadorRiesgo('POL-1'); e2=EvaluadorRiesgo('POL-2'); e1.anotar(0.5); e2.anotar(0.9); print(len(e1.historial), len(e2.historial), e1.historial is e2.historial)"` | `2 2 True` | *(pendiente — se llena en la Parte B)* |
| H12 | `requirements.txt` lista sus 7 paquetes (`fastapi`, `uvicorn`, `pydantic`, `scikit-learn`, `numpy`, `pytest`, `httpx`) sin ninguna versión fijada con `==`; instalar hoy o dentro de seis meses puede traer versiones distintas y romper el entorno | El archivo se escribió a mano listando solo los nombres de los paquetes, sin correr `pip freeze` (o equivalente) para fijar la versión exacta instalada al construir el proyecto | M2 · 5. requirements.txt y la reproducibilidad (Material de Clase) | `6a91db1` | `grep -c "==" requirements.txt` | `0` | *(pendiente — se llena en la Parte B)* |


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
