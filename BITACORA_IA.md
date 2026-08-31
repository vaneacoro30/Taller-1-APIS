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

## Aceptado

| # | Qué propuso la IA | Por qué lo aceptamos | Qué cambiamos antes de usarlo |
|---|-------------------|----------------------|-------------------------------|
| 1 | Identificó 11 posibles defectos en el servicio (arranque con `--reload`, secretos versionados en `config.py`, exportación con `pickle`, validación manual con `assert`, errores con status 200, modelo cargado dentro del handler, sin `/health`, decorador sin `functools.wraps` que traga excepciones, `historial` como atributo de clase compartido, `requirements.txt` sin versionar) y 3 defectos en `ia_propuesta.py` (validador sin `return`, `time.sleep` bloqueando la corrutina, regex de correo demasiado estricto) | Los hallazgos son coherentes con las buenas prácticas de los módulos 1 a 5 del curso y se verificaron leyendo el código directamente, no solo aceptando la explicación de la IA | Ninguno — se usaron tal cual como punto de partida del diagnóstico de la Parte A |

## Rechazado

| # | Qué propuso la IA | Por qué lo rechazamos | Qué hicimos en su lugar |
|---|-------------------|-----------------------|-------------------------|
| 1 | Crear el tag `v0-semilla` apuntando al commit semilla para citar la etiqueta tal como la nombra el enunciado | El enunciado permite usar el SHA directamente cuando el tag no existe, y crear el tag ahora sería artificial: se supone que marca el estado "tal como se lo entregamos", no algo agregado después. Tampoco aporta nada distinto a nivel funcional | Usamos el SHA `6a91db1` directamente en la tabla de HALLAZGOS.md, como permite el enunciado |
