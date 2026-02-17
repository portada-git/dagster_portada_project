from dagster import run_failure_sensor, RunFailureSensorContext, DagsterEventType
import os


def create_failure_sensor(job_list, sensor_name):
    """
    Crea un sensor que monitorea fallos en los jobs especificados.
    
    Args:
        job_list: Lista de jobs a monitorear
        sensor_name: Nombre del sensor
    """
    # Extraer nombres de jobs (Dagster espera strings, no objetos)
    job_names = [job.name for job in job_list]
    
    @run_failure_sensor(
        monitored_jobs=job_names,
        name=sensor_name,
        minimum_interval_seconds=30
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
            f"⚠️ Error: {error_msg[:500]}"
        )
        
        # 5. IMPORTANTE: Registrar en logs (esto hace que el sensor sea visible)
        context.log.error(f"🚨 Sensor activado por fallo en {asset_actual}")
        context.log.error(missatge)
        
        
        # 7. Opcional: Guardar en archivo de log
        try:
            log_dir = "logs/sensor_failures"
            os.makedirs(log_dir, exist_ok=True)
            log_file = f"{log_dir}/failure_{run_id}.txt"
            with open(log_file, 'w') as f:
                f.write(missatge)
                f.write("\n\n=== Metadata de assets anteriores ===\n")
                for record in records:
                    f.write(f"\nAsset: {record.event_log_entry.dagster_event.asset_key}\n")
                    if hasattr(record.event_log_entry.dagster_event, 'step_materialization_data'):
                        metadata = record.event_log_entry.dagster_event.step_materialization_data.materialization.metadata
                        f.write(f"Metadata: {metadata}\n")
            context.log.info(f"📝 Error guardado en {log_file}")
        except Exception as e:
            context.log.warning(f"⚠️ No se pudo guardar log en archivo: {str(e)}")
    
    return ingestion_error_sensor
