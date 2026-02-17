from dagster import asset, AssetIn, op, AssetExecutionContext
import logging
import redis

from portada_data_layer.portada_ingestion import BoatFactIngestion

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig, RedisClient

logger = logging.getLogger("boat_fact_dagster")

@asset
def ingested_entry_file(context, datalayer: DeltaDataLayerResource) -> dict:
    """Read local JSON file"""
    local_path = context.run_config["ops"]["ingested_entry_file"]["config"]["local_path"]
    user = context.run_config["ops"]["ingested_entry_file"]["config"]["user"]
    print(datalayer)
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    data, dest_path = layer.copy_ingested_raw_data("ship_entries", local_path=local_path, return_dest_path=True, user=user)
    context.log.info(f"Llegits {len(data)} registres de {local_path}")
    return {"local_path": local_path, "source_path": dest_path, "data_json_array": data}


@asset(ins={"data": AssetIn("ingested_entry_file")})
def raw_entries(context: AssetExecutionContext, data, datalayer: DeltaDataLayerResource, redis_config: RedisConfig) -> str:
    """Copia el fitxer al Data Lake (ingesta)"""
    user = context.run_config["ops"]["ingested_entry_file"]["config"]["user"]
    layer = datalayer.get_boat_fact_layer()
    layer.set_sequencer_params(redis_config.host, redis_config.port, 1)
    layer.start_session()
    layer.save_raw_data("ship_entries", data=data, user=user)
    return data["local_path"]


@asset(ins={"path": AssetIn("raw_entries")})
def update_data_base_for_entry(context: AssetExecutionContext, path, redis_config: RedisConfig) -> None:
    redis_client = RedisConfig.get_redis_client()
    file_found = redis_client.update_file(path, RedisClient.PROCESSED_STATUS)

    if file_found:
        context.log.info(f"Updated status to Processing for entity file: {path}")
    else:
        context.log.warning(f"Entity file not found in Redis with path: {path}")



