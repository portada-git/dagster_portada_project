from dagster import run_failure_sensor, RunFailureSensorContext, DagsterEventType
import os


def create_failure_sensor(job_list, sensor_name, callback):
    """
    Crea un sensor que monitorea fallos en los jobs especificados.
    
    Args:
        :param job_list: Lista de jobs a monitorear
        :param sensor_name: Nombre del sensor
        :param callback: callback to call if error
    """

    @run_failure_sensor(
        monitored_jobs=job_list,
        name=sensor_name,
        minimum_interval_seconds=30
    )
    def ingestion_error_sensor(context: RunFailureSensorContext):
        """Sensor que se activa cuando falla un job de ingesta"""

        # 1. Obtener ID del Run
        run_id = context.dagster_run.run_id

        # 2. MÉTODO ROBUSTO: Obtener estadísticas de los pasos
        # Esto devuelve objetos RunStepStats, no logs crudos.
        step_stats = context.instance.get_run_step_stats(run_id)

        # Filtramos por estado 'FAILURE' (buscamos el string para evitar problemas de import)
        failed_steps = [
            stat.step_key
            for stat in step_stats
            if stat.status.value == 'FAILURE'
        ]

        # 3. Determinar el nombre del asset
        if failed_steps:
            asset_actual = failed_steps[0]  # Tomamos el primero que falló
        else:
            # Si la lista está vacía, es que falló el Run antes de ejecutar un step
            # o context.failure_event.step_key podría tenerlo
            asset_actual = context.failure_event.step_key or "Fallo de Sistema (sin step)"

        # 4. Obtener mensaje de error
        error_msg = context.failure_event.message or "Error desconocido"

        # 5. Configuración y Notificación
        run_config = context.dagster_run.run_config

        # Solo intentamos buscar config si tenemos un nombre de asset real
        config_usada = "N/A"
        if asset_actual and asset_actual != "Fallo de Sistema (sin step)":
            config_usada = run_config.get('ops', {}).get(asset_actual, {})

        # Recuperamos los logs de fallo del paso
        records = context.instance.get_records_for_run(
            run_id=run_id,
            of_type=DagsterEventType.STEP_FAILURE
        )

        exception_msg = "No se ha podido recuperar la excepción detallada."
        error_data = None

        # if records:
        #     # records[0] es el primer EventLogRecord
        #     # .event_log_entry es el objeto que contiene el evento de Dagster
        #     # .dagster_event contiene los datos específicos del fallo
        #     dagster_event = records[0].event_log_entry.dagster_event
        #
        #     if dagster_event and dagster_event.event_specific_data:
        #         # El objeto 'StepFailureData' tiene un atributo 'error' (un PythonCaughtException)
        #         error_data = dagster_event.event_specific_data.error
        #         exception_msg = error_data.message
        #
        #         # O incluso el TRACEBACK completo (el error de Python con línea y archivo):
        #         # full_traceback = error_data.cause.stack if error_data.cause else error_data.stack

        param = {
            "asset": asset_actual,
            "run_config": run_config,
            "error": error_data,
            "error_msg": exception_msg
        }

        callback(param, context.log)

        # Construir mensaje
        message = (
            f" Fallada en job de ingesta\n"
            f" Run ID: {run_id}\n"
            f" Asset: {asset_actual}\n"
            f" Config: {run_config}\n"
            f" Error: {error_msg[:500]}\n"
            f"records: {records}\n"
            f"records[0]: {records[0]}\n"
        )
        
        # IMPORTANTE: Registrar en logs (esto hace que el sensor sea visible)
        context.log.error(f"🚨 Sensor activado por fallo en {asset_actual}")
        context.log.error(message)
    
    return ingestion_error_sensor
