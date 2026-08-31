# Bitácora de uso de IA

**Integrantes:** Vanessa Acosta, Mateo Ramos
**Herramientas usadas:** Claude (Sonnet 5)

> Las tres secciones son obligatorias. **`## Rechazado` es la que se califica.**
> Una bitácora que solo lista prompts aceptados vale la mitad.

## Prompts

| # | Parte | Quién | Prompt (resumido si es largo) |
|---|-------|-------|-------------------------------|
| 1 | A | Vanessa | Evalúa este código y dime qué errores observas que tiene, teniendo en cuenta las buenas prácticas en código |
| 2 | A | Vanessa | ¿Cuál es la diferencia entre usar el SHA `6a91db1` directo o crear el tag `v0-semilla` para documentar el hallazgo en HALLAZGOS.md? |
| 3 | Todas | Vanessa | "esto quedo cargado en mi rama, cómo lo cargo a la rama principal o como hago para que mi compañero ya lo vea reflejado? no entiendo muy bien el tema de las ramas" |
| 4 | Todas | Vanessa | "tengo un push que cargue en una rama mia, ahora quiero pasarlo a rama principal, cómo lo hago?" |
| 5 | B | Vanessa | "Más allá de que se vea raro al imprimir, ¿qué problema real trae que puntuar.__name__ diga envoltura en vez de puntuar?" |
| 6 | B | Vanessa | "Si el decorador no atrapara la excepción, ¿qué pasaría con la petición HTTP en /score? ¿Qué código de estado devolvería FastAPI?" |
| 7 | B | Vanessa | "¿Por qué historial = [] a nivel de clase termina compartido entre instancias, en vez de que cada EvaluadorRiesgo tenga el suyo?" |

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | Identificó 11 posibles defectos en el servicio (arranque con `--reload`, secretos versionados en `config.py`, exportación con `pickle`, validación manual con `assert`, errores con status 200, modelo cargado dentro del handler, sin `/health`, decorador sin `functools.wraps` que traga excepciones, `historial` como atributo de clase compartido, `requirements.txt` sin versionar) y 3 defectos en `ia_propuesta.py` (validador sin `return`, `time.sleep` bloqueando la corrutina, regex de correo demasiado estricto) | Los hallazgos son coherentes con las buenas prácticas de los módulos 1 a 5 del curso y se verificaron leyendo el código directamente, no solo aceptando la explicación de la IA | Ninguno — se usaron tal cual como punto de partida del diagnóstico de la Parte A |
| 2 | Explicó la diferencia entre una rama local y `main`, y propuso fusionar `vane` → `main` mediante Pull Request en GitHub | Deja trazabilidad del cambio y es el flujo que recomienda el curso para trabajo colaborativo (M1 · Git y GitHub) | Ninguno — se siguieron los pasos tal cual |
| 3 | Al detectar que Mateo ya había usado los IDs `H2`-`H7` en su rama, propuso renumerar nuestros hallazgos a `H8`-`H12` en vez de pedirle a Mateo que cambiara los suyos | Evita reescribir trabajo ya hecho por un compañero y deja la tabla final ordenada sin huecos | Ninguno |
| 4 | Explicó que perder `__name__`/`__doc__` (H9) no es solo estético: rompe la lectura de logs y stack traces (varios métodos decorados se ven todos como `envoltura`) y cualquier herramienta que dependa de `__wrapped__`/`__doc__`/la firma real | Es la razón concreta detrás de la restricción B9 del enunciado y justifica por qué `functools.wraps` no es un detalle cosmético | Ninguno — se usará como criterio al agregar `@functools.wraps(func)` en la Parte B |
| 5 | Explicó que, sin el `except` que traga la excepción (H10), un payload inválido en `/score` propagaría un error no controlado que Starlette convertiría en un `500` genérico sin detalle útil; la corrección real es validar la entrada con un `BaseModel` de Pydantic *antes* de que llegue a `puntuar`, para que dé `422` con el detalle del campo inválido | Conecta el defecto de `utilidades.py` (B9) con la validación de entrada de `main.py` (B5), y aclara que la corrección no es solo "quitar el try/except" | Ninguno — sirve de criterio para la Parte B: el decorador dejará de devolver `None` en silencio, y `main.py` validará la entrada con `BaseModel` |
| 6 | Explicó el mecanismo de resolución de atributos de Python (H11): `self.historial` busca primero en el `__dict__` de la instancia y, al no encontrarlo, cae al `__dict__` de la clase, donde vive la lista compartida; `anotar()` la muta con `.append()` sin haber creado nunca un atributo propio en `self` | Es la explicación técnica exacta de por qué ocurre H11 y señala la corrección correcta sin tocar el constructor exigido por el enunciado (`EvaluadorRiesgo(poliza)`) | Ninguno — se aplicará en la Parte B: `self.historial = []` dentro de `__init__`, dejando `umbral` como atributo de clase porque ese sí debe compartirse |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Crear el tag `v0-semilla` apuntando al commit semilla para citar la etiqueta tal como la nombra el enunciado | El enunciado permite usar el SHA directamente cuando el tag no existe, y crear el tag ahora sería artificial: se supone que marca el estado "tal como se lo entregamos", no algo agregado después. Tampoco aporta nada distinto a nivel funcional | Usamos el SHA `6a91db1` directamente en la tabla de HALLAZGOS.md, como permite el enunciado |
| 2 | Al ver que Mateo había creado el tag `v0-semilla` (que no existía cuando decidimos usar el SHA), preguntó si queríamos cambiar la fila `H8` para usar `v0-semilla` por consistencia con las filas de Mateo | Cambiarlo habría contradicho la justificación ya registrada en la fila 1 de esta tabla, y el enunciado permite el SHA sin exigir uniformidad entre integrantes | Se dejó la fila `H8` con el SHA `6a91db1` |
| 3 | Propuso dos caminos para pasar la rama a `main`: crear un Pull Request en GitHub, o hacer merge directo local (`git merge` + `git push`) sin pasar por revisión | Preferimos dejar trazabilidad y un punto de revisión antes de fusionar a `main`, en vez de fusionar directo sin registro visible | Se usó el flujo de Pull Request (`compare/main...vane` → Create → Merge) para todas las fusiones de esta rama |
