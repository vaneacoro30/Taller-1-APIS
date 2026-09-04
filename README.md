# riesgo-api-v0

Servicio de puntuación de siniestros de la Aseguradora Santo Tomás.
Recibe los datos de una póliza y devuelve la probabilidad de que el siniestro
declarado termine en un pago alto.

## Instalación

```bash
python -m venv venv
venv\Scripts\activate        # En Windows (PowerShell/CMD)
# source venv/bin/activate   # En Linux/macOS
pip install -r requirements.txt
```

Copien `.env.example` a `.env` y completen los valores reales de `API_KEY` y
`CLAVE_FIRMA` (`.env` está en `.gitignore`, no se versiona). El servicio arranca
igual sin ese archivo —`config.py` los lee con `os.getenv(...)`, nunca con un
secreto hardcodeado— pero crearlo es buena práctica para cuando esas variables
se conecten a lógica real.

```bash
cp .env.example .env   # o copy .env.example .env  en Windows CMD
```

El modelo entrenado (`modelo.pkl`) viene en el repositorio y se carga una sola
vez al iniciar el servicio.

## Puesta en marcha

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

Este es el arranque de producción: varios procesos (`--workers`) y **sin
`--reload`**. La recarga en caliente (`--reload`) es solo para desarrollo local
—vigila el sistema de archivos y reinicia ante cualquier cambio—, no está
endurecida frente a un cliente hostil y no gestiona varios procesos.

## Endpoints

| Método | Ruta | Qué hace |
|---|---|---|
| POST | `/score` | Puntúa una póliza |
| GET | `/historial` | Evaluaciones hechas |
| GET | `/siniestros/{id}` | Consulta un siniestro |
| GET | `/exportar` | Exporta el histórico para el equipo de actuaría |
| GET | `/ping` | Comprobación rápida |
| GET | `/consulta-archivo` | Cuenta los registros del archivo de siniestros |
| GET | `/servicio-externo` | Consulta la tarifa de referencia del reasegurador |
| GET | `/calculo-pesado` | Recalcula la reserva agregada |

### Ejemplo

```bash
curl -X POST localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"poliza": "POL-2026-0413", "monto": 4200000, "antiguedad": 3, "siniestros_previos": 1}'
```

```json
{"poliza": "POL-2026-0413", "puntaje": 0.61, "alto_riesgo": false}
```

Una entrada inválida (falta un campo, `monto` no positivo, `antiguedad`
negativa) devuelve **422** con el detalle de validación, no 200 con un error en
el cuerpo.

## Notas

- La configuración sensible (claves, secretos) se lee de variables de entorno, no
  se versiona en el repositorio.
- El histórico se exporta en **JSON** (`GET /exportar`), no con `pickle`.
- `GET /health` responde 200 para comprobaciones de estado.
