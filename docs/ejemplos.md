# Ejemplos Prácticos

## Ejemplo 1: Ingesta Básica de Noticias

### Escenario
Tienes un archivo JSON con noticias del día y quieres ingestarlo en el Data Lake.

### Archivo de Datos
```json
// /data/news/2024-01-15.json
[
  {
    "id": "news_001",
    "title": "Nueva tecnología en navegación",
    "content": "...",
    "published_date": "2024-01-15",
    "source": "Maritime News"
  },
  {
    "id": "news_002",
    "title": "Avances en propulsión marina",
    "content": "...",
    "published_date": "2024-01-15",
    "source": "Tech Marine"
  }
]
```

### Ejecución desde Dagster UI

1. Abre http://localhost:3000
2. Ve a "Jobs" → "entry_ingestion"
3. Haz clic en "Launch Run"
4. Configura:

```yaml
ops:
  ingested_entry_file:
    config:
      local_path: "/data/news/2024-01-15.json"
      user: "data_engineer"
```

5. Haz clic en "Launch Run"

### Ejecución desde Python

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

print(f"Success: {result.success}")
```

### Verificación en Redis

```bash
redis-cli
> KEYS file:*
> HGETALL file:1
```

---

## Ejemplo 2: Ingesta de Entidades

### Escenario
Tienes un archivo con información de personas relevantes en el sector marítimo.

### Archivo de Datos
```json
// /data/entities/persons.json
[
  {
    "id": "person_001",
    "name": "John Smith",
    "role": "Captain",
    "organization": "Maritime Corp",
    "expertise": ["navigation", "safety"]
  },
  {
    "id": "person_002",
    "name": "Jane Doe",
    "role": "Engineer",
    "organization": "Tech Marine",
    "expertise": ["propulsion", "maintenance"]
  }
]
```

### Configuración

```yaml
ops:
  ingested_entity_file:
    config:
      local_path: "/data/entities/persons.json"
      entity_type: "persons"
```

### Ejecución

```python
from dagster_portada_project.definitions import defs

result = defs.get_job_def("entity_ingestion").execute_in_process(
    run_config={
        "ops": {
            "ingested_entity_file": {
                "config": {
                    "local_path": "/data/entities/persons.json",
                    "entity_type": "persons"
                }
            }
        }
    }
)
```

---

## Ejemplo 3: Procesamiento por Lotes

### Escenario
Procesar múltiples archivos de noticias de diferentes días.

### Script de Procesamiento

```python
from dagster_portada_project.definitions import defs
from datetime import datetime, timedelta
import os

def process_daily_news(start_date, end_date):
    """Procesa noticias de un rango de fechas"""
    current_date = start_date
    results = []
    
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        file_path = f"/data/news/{date_str}.json"
        
        # Verificar si el archivo existe
        if not os.path.exists(file_path):
            print(f"Archivo no encontrado: {file_path}")
            current_date += timedelta(days=1)
            continue
        
        # Ejecutar job
        print(f"Procesando {date_str}...")
        result = defs.get_job_def("entry_ingestion").execute_in_process(
            run_config={
                "ops": {
                    "ingested_entry_file": {
                        "config": {
                            "local_path": file_path,
                            "user": "batch_processor"
                        }
                    }
                }
            }
        )
        
        results.append({
            "date": date_str,
            "success": result.success,
            "run_id": result.run_id
        })
        
        current_date += timedelta(days=1)
    
    return results

# Uso
start = datetime(2024, 1, 1)
end = datetime(2024, 1, 31)
results = process_daily_news(start, end)

# Resumen
successful = sum(1 for r in results if r["success"])
print(f"Procesados: {len(results)}, Exitosos: {successful}")
```

---

## Ejemplo 4: Configuración con Redis Personalizado

### Escenario
Usar un servidor Redis diferente para un job específico.

### Configuración

```yaml
ops:
  ingested_entry_file:
    config:
      local_path: "/data/news/special.json"
      user: "admin"
      redis_config:
        host: "redis-prod.example.com"
        port: "6380"
```

### Código

```python
result = defs.get_job_def("entry_ingestion").execute_in_process(
    run_config={
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": "/data/news/special.json",
                    "user": "admin",
                    "redis_config": {
                        "host": "redis-prod.example.com",
                        "port": "6380"
                    }
                }
            }
        }
    }
)
```

---

## Ejemplo 5: Crear un Asset Personalizado

### Escenario
Crear un asset que valida la calidad de los datos antes de la ingesta.

### Código

```python
# dagster_portada_project/assets/validation_assets.py

from dagster import asset, AssetIn, AssetExecutionContext, Output, MetadataValue
import json

@asset
def validated_entry_file(
    context: AssetExecutionContext
) -> dict:
    """Valida el archivo de entrada antes de procesarlo"""
    local_path = context.run_config["ops"]["validated_entry_file"]["config"]["local_path"]
    
    # Leer archivo
    with open(local_path, 'r') as f:
        data = json.load(f)
    
    # Validaciones
    errors = []
    warnings = []
    
    for i, entry in enumerate(data):
        # Validar campos requeridos
        if "id" not in entry:
            errors.append(f"Entrada {i}: falta campo 'id'")
        if "title" not in entry:
            errors.append(f"Entrada {i}: falta campo 'title'")
        
        # Validar tipos
        if "published_date" in entry:
            try:
                datetime.strptime(entry["published_date"], "%Y-%m-%d")
            except ValueError:
                warnings.append(f"Entrada {i}: formato de fecha inválido")
    
    # Registrar resultados
    context.log.info(f"Validadas {len(data)} entradas")
    context.log.info(f"Errores: {len(errors)}, Advertencias: {len(warnings)}")
    
    if errors:
        context.log.error(f"Errores de validación: {errors}")
        raise ValueError(f"Validación fallida: {len(errors)} errores encontrados")
    
    if warnings:
        context.log.warning(f"Advertencias: {warnings}")
    
    return Output(
        value={"local_path": local_path, "data": data},
        metadata={
            "num_entries": MetadataValue.int(len(data)),
            "num_warnings": MetadataValue.int(len(warnings)),
            "validation_status": MetadataValue.text("passed")
        }
    )

@asset(ins={"validated_data": AssetIn("validated_entry_file")})
def ingested_validated_entries(
    context: AssetExecutionContext,
    validated_data: dict,
    datalayer: DeltaDataLayerResource
):
    """Ingesta datos validados"""
    user = context.run_config["ops"]["validated_entry_file"]["config"]["user"]
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    
    data, dest_path = layer.copy_ingested_raw_data(
        "ship_entries",
        local_path=validated_data["local_path"],
        return_dest_path=True,
        user=user
    )
    
    return {"source_path": dest_path, "data": data}
```

### Registrar Assets

```python
# definitions.py
from dagster_portada_project.assets import validation_assets

validation_assets_list = load_assets_from_modules(
    [validation_assets], 
    group_name="validation"
)

defs = Definitions(
    assets=[
        *boat_fact_all_assets,
        *entity_all_assets,
        *validation_assets_list
    ],
    # ...
)
```

---

## Ejemplo 6: Schedule Automático

### Escenario
Ejecutar ingesta de noticias automáticamente cada día a las 2 AM.

### Código

```python
# dagster_portada_project/schedules/daily_schedules.py

from dagster import schedule, ScheduleDefinition
from datetime import datetime
import os

@schedule(
    cron_schedule="0 2 * * *",  # Cada día a las 2 AM
    job_name="entry_ingestion",
    execution_timezone="Europe/Madrid"
)
def daily_news_ingestion(context):
    """Schedule para ingesta diaria de noticias"""
    # Generar path basado en la fecha
    date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    file_path = f"/data/news/{date}.json"
    
    # Verificar si el archivo existe
    if not os.path.exists(file_path):
        context.log.warning(f"Archivo no encontrado: {file_path}")
        return {}
    
    return {
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": file_path,
                    "user": "scheduler"
                }
            }
        }
    }
```

### Registrar Schedule

```python
# definitions.py
from dagster_portada_project.schedules.daily_schedules import daily_news_ingestion

defs = Definitions(
    assets=[...],
    resources={...},
    jobs=[entry_ingestion, entity_ingestion],
    sensors=[ingestion_error_sensor],
    schedules=[daily_news_ingestion]
)
```

---

## Ejemplo 7: Monitoreo con Metadata

### Escenario
Registrar estadísticas detalladas durante la ingesta.

### Código

```python
from dagster import asset, Output, MetadataValue
import time

@asset
def monitored_ingestion(
    context: AssetExecutionContext,
    datalayer: DeltaDataLayerResource
):
    """Asset con monitoreo detallado"""
    start_time = time.time()
    
    local_path = context.run_config["ops"]["monitored_ingestion"]["config"]["local_path"]
    user = context.run_config["ops"]["monitored_ingestion"]["config"]["user"]
    
    # Leer datos
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    
    data, dest_path = layer.copy_ingested_raw_data(
        "ship_entries",
        local_path=local_path,
        return_dest_path=True,
        user=user
    )
    
    # Calcular estadísticas
    elapsed_time = time.time() - start_time
    num_records = len(data)
    avg_time_per_record = elapsed_time / num_records if num_records > 0 else 0
    
    # Registrar metadata
    return Output(
        value={"local_path": local_path, "data": data},
        metadata={
            "num_records": MetadataValue.int(num_records),
            "processing_time_seconds": MetadataValue.float(elapsed_time),
            "avg_time_per_record_ms": MetadataValue.float(avg_time_per_record * 1000),
            "source_file": MetadataValue.path(local_path),
            "destination_path": MetadataValue.path(dest_path),
            "user": MetadataValue.text(user),
            "timestamp": MetadataValue.text(datetime.now().isoformat())
        }
    )
```

---

## Ejemplo 8: Testing de Assets

### Escenario
Crear tests para validar el comportamiento de los assets.

### Código

```python
# dagster_portada_project_tests/test_ingestion.py

import pytest
import json
import tempfile
from dagster import build_asset_context, materialize
from dagster_portada_project.assets.boat_fact_ingestion_assets import ingested_entry_file

@pytest.fixture
def sample_data():
    """Datos de prueba"""
    return [
        {
            "id": "test_001",
            "title": "Test News",
            "content": "Test content",
            "published_date": "2024-01-15"
        }
    ]

@pytest.fixture
def temp_json_file(sample_data):
    """Crear archivo temporal con datos de prueba"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        return f.name

def test_ingested_entry_file(temp_json_file, mock_datalayer):
    """Test del asset ingested_entry_file"""
    context = build_asset_context(
        run_config={
            "ops": {
                "ingested_entry_file": {
                    "config": {
                        "local_path": temp_json_file,
                        "user": "test_user"
                    }
                }
            }
        },
        resources={"datalayer": mock_datalayer}
    )
    
    result = ingested_entry_file(context, mock_datalayer)
    
    assert result is not None
    assert "local_path" in result
    assert "data_json_array" in result
    assert len(result["data_json_array"]) == 1
    assert result["data_json_array"][0]["id"] == "test_001"

def test_full_pipeline(temp_json_file, mock_datalayer, mock_redis):
    """Test del pipeline completo"""
    from dagster_portada_project.assets import boat_fact_ingestion_assets
    
    result = materialize(
        load_assets_from_modules([boat_fact_ingestion_assets]),
        run_config={
            "ops": {
                "ingested_entry_file": {
                    "config": {
                        "local_path": temp_json_file,
                        "user": "test_user"
                    }
                }
            }
        },
        resources={
            "datalayer": mock_datalayer,
            "redis_config": mock_redis
        }
    )
    
    assert result.success
```

---

## Ejemplo 9: Integración con Slack

### Escenario
Enviar notificaciones a Slack cuando hay fallos.

### Código

```python
# dagster_portada_project/sensors/slack_sensors.py

from dagster import run_failure_sensor, RunFailureSensorContext
import requests
import os

@run_failure_sensor(
    monitored_jobs=["entry_ingestion", "entity_ingestion"],
    name="slack_failure_sensor"
)
def slack_failure_notification(context: RunFailureSensorContext):
    """Envía notificaciones a Slack en caso de fallo"""
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    if not slack_webhook_url:
        context.log.warning("SLACK_WEBHOOK_URL no configurado")
        return
    
    # Información del fallo
    asset_name = context.failure_event.step_key
    error_msg = context.failure_event.message
    run_id = context.dagster_run.run_id
    
    # Construir mensaje
    message = {
        "text": f"🚨 Fallo en Dagster Pipeline",
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🚨 Fallo en Pipeline de Ingesta"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Asset:*\n{asset_name}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Run ID:*\n{run_id}"
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Error:*\n```{error_msg[:500]}```"
                }
            }
        ]
    }
    
    # Enviar a Slack
    response = requests.post(slack_webhook_url, json=message)
    
    if response.status_code == 200:
        context.log.info("Notificación enviada a Slack")
    else:
        context.log.error(f"Error al enviar a Slack: {response.status_code}")
```

### Configuración

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

---

## Recursos Adicionales

- Ver [Guía de Desarrollo](desarrollo.md) para más información sobre desarrollo
- Ver [API Reference](api-reference.md) para documentación completa de la API
- Ver [Jobs y Sensors](jobs-sensors.md) para más detalles sobre orquestación
