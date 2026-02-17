from dagster import run_failure_sensor, RunFailureSensorContext, DagsterEventType


def create_failure_sensor(job_list, sensor_name):
    @run_failure_sensor(monitored_jobs=job_list, name=sensor_name)
    def ingestion_error_sensor(context: RunFailureSensorContext):
        # 1. Recuperar tota la CONFIGURACIÓ (Punt 1 de cada asset)
        run_config = context.dagster_run.run_config

        # 2. Recuperar l'ERROR i l'asset que ha fallat
        asset_actual = context.failure_event.step_key
        error_msg = context.failure_event.message

        # 3. Recuperar valors de RETORN (Punt 2)
        # Atenció: Només podràs veure el valor si el primer asset el va registrar com a metadata.
        # Si no, hauries de carregar-lo manualment des del teu storage (S3/Base de dades).

        # Intentem buscar metadata de l'asset 1 si ha fallat el 2 o el 3
        # Això requereix consultar l'històric d'esdeveniments:
        records = context.instance.get_records_for_run(
            run_id=context.dagster_run.run_id,
            of_type=DagsterEventType.ASSET_MATERIALIZATION
        )

        # 4. Notificació de Slack amb el resum
        missatge = (
            f"❌ Fallada a l'asset: {asset_actual}\n"
            f"⚙️ Config emprada: {run_config.get('ops', {}).get(asset_actual, {})}\n"
            f"⚠️ Error: {error_msg}"
        )

    return ingestion_error_sensor
