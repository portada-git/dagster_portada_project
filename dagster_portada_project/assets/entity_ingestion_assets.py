from dagster import asset, AssetIn, op, AssetExecutionContext
import logging
import redis

from portada_data_layer.portada_ingestion import BoatFactIngestion

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig, RedisClient

logger = logging.getLogger("boat_fact_dagster")


@asset
def ingested_entity_file(context, datalayer: DeltaDataLayerResource) -> dict:
    """Read local JSON file"""
    local_path = context.run_config["ops"]["ingested_entity_file"]["config"]["local_path"]
    entity_type = context.run_config["ops"]["ingested_entity_file"]["config"]["entity_type"]
    print(datalayer)
    layer = datalayer.get_know_entities_layer()
    layer.start_session()
    data, dest_path = layer.copy_ingested_raw_data(entity_type, local_path=local_path, return_dest_path=True)
    context.log.info(f"Llegits {len(data)} registres de {local_path}")
    return {"local_path": local_path, "source_path": dest_path, "data": data}


@asset(ins={"data": AssetIn("ingested_entity_file")})
def raw_entities(context: AssetExecutionContext, data, datalayer: DeltaDataLayerResource) -> str:
    """Copia el fitxer al Data Lake (ingesta)"""
    type = context.run_config["ops"]["ingested_entity_file"]["config"]["entity_type"]
    layer = datalayer.get_know_entities_layer()
    layer.start_session()
    layer.save_raw_data(type, data=data)
    return data["local_path"]


@asset(ins={"path": AssetIn("raw_entities")})
def update_data_base_for_entity(context: AssetExecutionContext, path, redis_config: RedisConfig) -> None:
    redis_client = RedisConfig.get_redis_client()
    file_found = redis_client.update_file(path, RedisClient.PROCESSED_STATUS)

    if file_found:
        context.log.info(f"Updated status to Processing for entity file: {path}")
    else:
        context.log.warning(f"Entity file not found in Redis with path:  {path}")

