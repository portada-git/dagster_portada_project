# Jobs y Sensors

## Jobs

Los Jobs en Dagster son colecciones de assets que se ejecutan juntos. Definen qué assets materializar y en qué orden.

### entry_ingestion

**Descripción:** Job que ejecuta el pipeline completo de ingesta de noticias (boat facts).

**Definición:**
```python
entry_ingestion = define_asset_job(
    name="entry_ingestion",
    selection="group:grup_boat_fact",
    tags={"process": "ingestion"},
)
```

**Assets Incluidos:**
- `ingested_entry_file`
- `raw_entries`
- `update_data_base_for_entry`

**Tags:**
- `process`: `ingestion`

#### Ejecución desde UI

1. Ve a la pestaña "Jobs"
2. Selecciona "entry_ingestion"
3. Haz clic en "Launch Run"
4. Proporciona la configuración:

```yaml
ops:
  ingested_entry_file:
    config:
      local_path: "/data/news/2024-01-15.json"
      user: "data_engineer"
```

5. Haz clic en "Launch Run"

#### Ejecución desde Python

```python
from dagster import execute_job
from dagster_portada_project.definitions import defs

result = defs.get_job_def("entry_ingestion").execute_in_process(
    run_config={
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": "/data/news/2024-01-15.json",
                    "user": "data_engineer"
                }
            }
        }
    }
)
```

---

### entity_ingestion

**Descripción:** Job que ejecuta el pipeline completo de ingesta de entidades conocidas.

**Definición:**
```python
entity_ingestion = define_asset_job(
    name="entity_ingestion",
    selection="group:grup_entity",
    tags={"process": "ingestion"},
)
```

**Assets Incluidos:**
- `ingested_entity_file`
- `raw_entities`
- `update_data_base_for_entity`

**Tags:**
- `process`: `ingestion`

#### Configuración de Ejemplo

```yaml
ops:
  ingested_entity_file:
    config:
      local_path: "/data/entities/persons.json"
      entity_type: "persons"
```

#### Tipos de Entidades

- `persons`: Personas
- `organizations`: Organizaciones
- `places`: Lugares
- Otros tipos según configuración del data layer

---

## Sensors

Los Sensors en Dagster son procesos que monitorean eventos y pueden lanzar runs automáticamente o enviar notificaciones.

### ingestion_error_sensor

**Descripción:** Sensor que monitorea fallos en los jobs de ingesta y prepara notificaciones.

**Tipo:** `run_failure_sensor`

**Jobs Monitoreados:**
- `entry_ingestion`
- `entity_ingestion`

#### Definición

```python
from dagster import run_failure_sensor, RunFailureSensorContext, DagsterEventType

def create_failure_sensor(job_list, sensor_name):
    @run_failure_sensor(monitored_jobs=job_list, name=sensor_name)
    def ingestion_error_sensor(context: RunFailureSensorContext):
        # 1. Recuperar configuración
        run_config = context.dagster_run.run_config

        # 2. Recuperar error y asset que falló
        asset_actual = context.failure_event.step_key
        error_msg = context.failure_event.message

        # 3. Recuperar valores de retorno de assets anteriores
        records = context.instance.get_records_for_run(
            run_id=context.dagster_run.run_id,
            of_type=DagsterEventType.ASSET_MATERIALIZATION
        )

        # 4. Preparar notificación
        missatge = (
            f"❌ Fallada a l'asset: {asset_actual}\n"
            f"⚙️ Config emprada: {run_config.get('ops', {}).get(asset_actual, {})}\n"
            f"⚠️ Error: {error_msg}"
        )
        
        # Aquí se podría enviar a Slack, email, etc.

    return ingestion_error_sensor
```

#### Información Capturada

1. **Configuración del Run:**
   - Todos los parámetros usados en el run
   - Configuración de cada asset

2. **Información del Fallo:**
   - Asset que falló
   - Mensaje de error completo
   - Stack trace

3. **Metadata de Assets Anteriores:**
   - Valores retornados por assets que se ejecutaron correctamente
   - Metadata registrado durante la ejecución

#### Uso del Contexto

```python
# Acceder a la configuración
run_config = context.dagster_run.run_config
local_path = run_config["ops"]["ingested_entry_file"]["config"]["local_path"]

# Acceder al error
asset_name = context.failure_event.step_key
error_message = context.failure_event.message

# Acceder a materializaciones previas
records = context.instance.get_records_for_run(
    run_id=context.dagster_run.run_id,
    of_type=DagsterEventType.ASSET_MATERIALIZATION
)

for record in records:
    asset_key = record.event_log_entry.dagster_event.asset_key
    metadata = record.event_log_entry.dagster_event.step_materialization_data.materialization.metadata
```

#### Integración con Slack

Para enviar notificaciones a Slack, puedes extender el sensor:

```python
import requests

@run_failure_sensor(monitored_jobs=job_list, name=sensor_name)
def ingestion_error_sensor(context: RunFailureSensorContext):
    # ... código existente ...
    
    # Enviar a Slack
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if slack_webhook_url:
        payload = {
            "text": missatge,
            "username": "Dagster Alert",
            "icon_emoji": ":warning:"
        }
        requests.post(slack_webhook_url, json=payload)
```

#### Activación del Sensor

Los sensores deben estar activados en Dagster:

1. **Desde UI:**
   - Ve a "Automation" → "Sensors"
   - Encuentra "error_sensor"
   - Activa el toggle

2. **Verificar Estado:**
   - El sensor debe mostrar estado "Running"
   - Requiere que el Dagster Daemon esté ejecutándose

3. **Dagster Daemon:**
   ```bash
   # El daemon se inicia automáticamente con:
   dagster dev
   
   # O manualmente:
   dagster-daemon run
   ```

---

## Schedules

Aunque el proyecto actual no incluye schedules, puedes añadirlos para ejecutar jobs periódicamente.

### Ejemplo de Schedule

```python
from dagster import schedule, ScheduleDefinition

@schedule(
    cron_schedule="0 2 * * *",  # Cada día a las 2 AM
    job=entry_ingestion,
    execution_timezone="Europe/Madrid"
)
def daily_entry_ingestion_schedule(context):
    # Generar configuración dinámica
    date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    
    return {
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": f"/data/news/{date}.json",
                    "user": "scheduler"
                }
            }
        }
    }
```

### Añadir Schedule a Definitions

```python
from dagster import Definitions

defs = Definitions(
    assets=[...],
    resources={...},
    jobs=[entry_ingestion, entity_ingestion],
    sensors=[ingestion_error_sensor],
    schedules=[daily_entry_ingestion_schedule]  # Añadir aquí
)
```

---

## Monitoreo y Alertas

### Logs de Ejecución

Todos los runs generan logs detallados:

```python
# En assets
context.log.info("Procesando archivo...")
context.log.warning("Archivo no encontrado en Redis")
context.log.error("Error al conectar a Spark")
```

### Metadata

Registra metadata adicional en assets:

```python
from dagster import Output, MetadataValue

@asset
def my_asset(context):
    # ... procesamiento ...
    
    return Output(
        value=result,
        metadata={
            "num_records": MetadataValue.int(len(data)),
            "file_size": MetadataValue.float(file_size_mb),
            "processing_time": MetadataValue.float(elapsed_time)
        }
    )
```

### Visualización en UI

- **Runs:** Historial completo de ejecuciones
- **Assets:** Estado de materialización
- **Sensors:** Estado y últimas ejecuciones
- **Logs:** Logs en tiempo real durante ejecución

---

## Buenas Prácticas

1. **Tags Descriptivos:** Usa tags para categorizar jobs
2. **Configuración Flexible:** Permite configuración dinámica en schedules
3. **Notificaciones:** Implementa notificaciones para fallos críticos
4. **Monitoreo:** Revisa regularmente el estado de sensors y schedules
5. **Testing:** Prueba jobs con datos de prueba antes de producción
6. **Documentación:** Documenta la configuración esperada para cada job
