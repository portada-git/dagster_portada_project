# Troubleshooting: Sensor de Errores No Se Activa

## Problemas Identificados

### 1. ⚠️ El sensor no retorna nada ni registra logs

**Problema:** El sensor actual no hace nada visible cuando se ejecuta. No retorna `RunRequest`, no envía notificaciones, y solo construye un mensaje que nunca se usa.

**Código actual:**
```python
missatge = (
    f"❌ Fallada a l'asset: {asset_actual}\n"
    f"⚙️ Config emprada: {run_config.get('ops', {}).get(asset_actual, {})}\n"
    f"⚠️ Error: {error_msg}"
)
# El mensaje se crea pero nunca se usa
```

**Solución:** Agregar logging o acción:
```python
# Opción 1: Registrar en logs
context.log.error(missatge)

# Opción 2: Enviar a Slack (si está configurado)
send_to_slack(missatge)

# Opción 3: Guardar en base de datos
save_error_to_db(missatge)
```

---

### 2. ⚠️ Parámetro incorrecto en `@run_failure_sensor`

**Problema:** Estás usando `monitored_jobs` pero según la documentación de Dagster, el parámetro correcto es `monitor_all_code_locations` o especificar jobs individuales.

**Código actual:**
```python
@run_failure_sensor(monitored_jobs=job_list, name=sensor_name)
```

**Solución correcta:**
```python
# Opción 1: Monitorear jobs específicos por nombre
@run_failure_sensor(
    monitor_all_code_locations=False,
    name=sensor_name,
    monitored_jobs=[job.name for job in job_list]  # Usar nombres, no objetos
)

# Opción 2: Monitorear todos los jobs
@run_failure_sensor(
    monitor_all_code_locations=True,
    name=sensor_name
)
```

---

### 3. ⚠️ El daemon de Dagster debe estar corriendo

**Verificación necesaria:**

```bash
# Verificar que el daemon está corriendo
dagster-daemon health

# O desde la UI de Dagster
# Ir a: Deployment > Daemons
# Verificar que "Sensor daemon" está en estado "Running"
```

**Si no está corriendo:**
```bash
# Iniciar con dagster dev (incluye daemon)
dagster dev

# O iniciar daemon manualmente
dagster-daemon run
```

---

### 4. ⚠️ El sensor debe estar activado en la UI

**Pasos para verificar:**
1. Abrir Dagster UI (http://localhost:3000)
2. Ir a "Automation" → "Sensors"
3. Buscar "error_sensor"
4. Verificar que el toggle está en "ON" (verde)
5. Revisar el estado: debe decir "Running"

---

### 5. ⚠️ Los jobs deben estar registrados correctamente

**Problema potencial:** Estás pasando objetos de job a `monitored_jobs`, pero Dagster espera nombres de jobs (strings).

**Verificación:**
```python
# En definitions.py, verificar que los jobs tienen nombres
print(entry_ingestion.name)  # Debe imprimir: "entry_ingestion"
print(entity_ingestion.name)  # Debe imprimir: "entity_ingestion"
```

---

## Solución Completa

### Archivo corregido: `ingestion_sensors.py`

```python
from dagster import run_failure_sensor, RunFailureSensorContext, DagsterEventType
import os


def create_failure_sensor(job_list, sensor_name):
    """
    Crea un sensor que monitorea fallos en los jobs especificados.
    
    Args:
        job_list: Lista de jobs a monitorear
        sensor_name: Nombre del sensor
    """
    # Extraer nombres de jobs
    job_names = [job.name for job in job_list]
    
    @run_failure_sensor(
        monitored_jobs=job_names,  # Usar nombres, no objetos
        name=sensor_name,
        minimum_interval_seconds=30  # Opcional: intervalo mínimo entre evaluaciones
    )
    def ingestion_error_sensor(context: RunFailureSensorContext):
        """Sensor que se activa cuando falla un job de ingesta"""
        
        # 1. Recuperar configuración
        run_config = context.dagster_run.run_config
        
        # 2. Recuperar error y asset que falló
        asset_actual = context.failure_event.step_key
        error_msg = context.failure_event.message
        run_id = context.dagster_run.run_id
        
        # 3. Recuperar metadata de assets anteriores
        records = context.instance.get_records_for_run(
            run_id=run_id,
            of_type=DagsterEventType.ASSET_MATERIALIZATION
        )
        
        # 4. Construir mensaje
        missatge = (
            f"❌ Fallada en job de ingesta\n"
            f"🔑 Run ID: {run_id}\n"
            f"📦 Asset: {asset_actual}\n"
            f"⚙️ Config: {run_config.get('ops', {}).get(asset_actual, {})}\n"
            f"⚠️ Error: {error_msg[:500]}"  # Limitar longitud
        )
        
        # 5. IMPORTANTE: Registrar en logs (mínimo)
        context.log.error(f"Sensor activado por fallo en {asset_actual}")
        context.log.error(missatge)
        
        # 6. Opcional: Enviar a Slack
        slack_webhook = os.getenv("SLACK_WEBHOOK_URL")
        if slack_webhook:
            try:
                import requests
                payload = {
                    "text": missatge,
                    "username": "Dagster Alert Bot",
                    "icon_emoji": ":warning:"
                }
                response = requests.post(slack_webhook, json=payload, timeout=10)
                if response.status_code == 200:
                    context.log.info("Notificación enviada a Slack")
                else:
                    context.log.warning(f"Error al enviar a Slack: {response.status_code}")
            except Exception as e:
                context.log.error(f"Error al enviar notificación a Slack: {str(e)}")
        
        # 7. Opcional: Guardar en archivo de log
        try:
            log_dir = "logs/sensor_failures"
            os.makedirs(log_dir, exist_ok=True)
            log_file = f"{log_dir}/failure_{run_id}.txt"
            with open(log_file, 'w') as f:
                f.write(missatge)
            context.log.info(f"Error guardado en {log_file}")
        except Exception as e:
            context.log.warning(f"No se pudo guardar log en archivo: {str(e)}")
        
        # NOTA: No retornar RunRequest para evitar loops infinitos
        # Si necesitas lanzar otro job, hazlo con cuidado
    
    return ingestion_error_sensor
```

---

## Checklist de Verificación

### ✅ Antes de ejecutar

- [ ] El daemon de Dagster está corriendo (`dagster-daemon health`)
- [ ] El sensor está registrado en `Definitions`
- [ ] Los jobs están correctamente definidos con nombres
- [ ] El sensor usa nombres de jobs, no objetos

### ✅ En la UI de Dagster

- [ ] El sensor aparece en "Automation" → "Sensors"
- [ ] El sensor está activado (toggle en ON)
- [ ] El estado del sensor es "Running"
- [ ] No hay errores en el historial de ticks del sensor

### ✅ Después de un fallo

- [ ] Revisar logs del sensor en "Automation" → "Sensors" → "error_sensor" → "Tick History"
- [ ] Verificar que el sensor se ejecutó (debe aparecer un tick)
- [ ] Revisar logs del run fallido en "Runs" → seleccionar run → "Logs"
- [ ] Buscar mensajes del sensor en los logs

---

## Comandos de Diagnóstico

### Verificar estado del daemon
```bash
dagster-daemon health
```

**Salida esperada:**
```
Daemon statuses:
  - SENSOR: Running
  - SCHEDULE: Running
  - RUN_QUEUE: Running
  - BACKFILL: Running
```

### Listar sensores
```bash
dagster sensor list
```

**Salida esperada:**
```
error_sensor [RUNNING]
```

### Ver logs del daemon
```bash
# Los logs del daemon suelen estar en:
tail -f $DAGSTER_HOME/logs/dagster-daemon.log
```

### Probar el sensor manualmente
```python
# Script de prueba: test_sensor.py
from dagster import build_run_status_sensor_context
from dagster_portada_project.definitions import defs

# Obtener el sensor
sensor = defs.get_sensor_def("error_sensor")

# Ejecutar manualmente (requiere un run_id de un run fallido)
# context = build_run_status_sensor_context(run_id="<run_id_fallido>")
# sensor.evaluate_tick(context)
```

---

## Prueba del Sensor

### 1. Crear un asset que falle intencionalmente

```python
# dagster_portada_project/assets/test_failure_asset.py

from dagster import asset

@asset
def failing_test_asset():
    """Asset que falla para probar el sensor"""
    raise Exception("Error intencional para probar el sensor")
```

### 2. Crear un job de prueba

```python
# En definitions.py
from dagster_portada_project.assets import test_failure_asset

test_assets = load_assets_from_modules([test_failure_asset], group_name="test")

test_failure_job = define_asset_job(
    name="test_failure_job",
    selection="group:test"
)

# Agregar a la lista de jobs monitoreados
jobs = [entity_ingestion, entry_ingestion, test_failure_job]
```

### 3. Ejecutar el job de prueba

1. Ir a "Jobs" → "test_failure_job"
2. Hacer clic en "Launch Run"
3. El job debería fallar
4. Ir a "Automation" → "Sensors" → "error_sensor"
5. Verificar que apareció un nuevo tick
6. Revisar los logs del tick

---

## Configuración Adicional Recomendada

### Variables de Entorno

```bash
# .env
DAGSTER_HOME=/path/to/dagster/home
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Configuración de Logging

```python
# dagster.yaml (en $DAGSTER_HOME)
python_logs:
  python_log_level: INFO
  dagster_handler_config:
    handlers:
      console:
        class: logging.StreamHandler
        level: INFO
```

---

## Problemas Comunes y Soluciones

### Problema: "Sensor no aparece en la UI"
**Solución:** Reiniciar Dagster
```bash
# Detener
Ctrl+C

# Reiniciar
dagster dev
```

### Problema: "Sensor en estado STOPPED"
**Solución:** Activar manualmente desde la UI o con CLI
```bash
dagster sensor start error_sensor
```

### Problema: "Daemon no está corriendo"
**Solución:** Iniciar daemon
```bash
dagster-daemon run
```

### Problema: "Sensor se ejecuta pero no hace nada"
**Solución:** Verificar que el sensor tiene logging o acciones
```python
# Agregar al menos esto:
context.log.error("Sensor activado!")
```

---

## Referencias

- [Dagster Sensors Documentation](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors)
- [Run Status Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors#run-status-sensors)
- [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon)
