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
| 3 | A | Mateo | Clonar el repositorio semilla, crear el entorno virtual, instalar dependencias y levantar el servicio para confirmar que arranca según el README |
| 4 | A | Mateo | Leer ENUNCIADO.md y el material de los módulos 1–5 del curso para identificar los defectos del servicio y proponer cómo dividir el trabajo de diagnóstico con la compañera de grupo |
| 5 | A / C / D | Mateo | Validar contra el código real y las secciones exactas del material del curso los 11 hallazgos, los 3 candidatos de la Parte C y los 3 defectos de `ia_propuesta.py` que había encontrado Vanessa |
| 6 | B | Mateo | Refactorizar `main.py` y `README.md` para la Parte B: validación con Pydantic (`BaseModel`/`Field`/validador), 422/404, `/exportar` en JSON, `/health`, modelo cargado al iniciar y arranque de producción sin `--reload` |

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | Identificó 11 posibles defectos en el servicio (arranque con `--reload`, secretos versionados en `config.py`, exportación con `pickle`, validación manual con `assert`, errores con status 200, modelo cargado dentro del handler, sin `/health`, decorador sin `functools.wraps` que traga excepciones, `historial` como atributo de clase compartido, `requirements.txt` sin versionar) y 3 defectos en `ia_propuesta.py` (validador sin `return`, `time.sleep` bloqueando la corrutina, regex de correo demasiado estricto) | Los hallazgos son coherentes con las buenas prácticas de los módulos 1 a 5 del curso y se verificaron leyendo el código directamente, no solo aceptando la explicación de la IA | Ninguno — se usaron tal cual como punto de partida del diagnóstico de la Parte A |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Crear el tag `v0-semilla` apuntando al commit semilla para citar la etiqueta tal como la nombra el enunciado | El enunciado permite usar el SHA directamente cuando el tag no existe, y crear el tag ahora sería artificial: se supone que marca el estado "tal como se lo entregamos", no algo agregado después. Tampoco aporta nada distinto a nivel funcional | Usamos el SHA `6a91db1` directamente en la tabla de HALLAZGOS.md, como permite el enunciado |
