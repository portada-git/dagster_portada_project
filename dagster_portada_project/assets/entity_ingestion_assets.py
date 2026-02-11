from dagster import asset, AssetIn, op, AssetExecutionContext
import logging
import redis

from portada_data_layer.portada_ingestion import BoatFactIngestion

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig

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
    calling_redis_cfg = context.run_config["ops"]["ingested_entity_file"]["config"]["redis_config"] if "redis_config" in context.run_config["ops"]["ingested_entity_file"]["config"] else None
    redis_host = redis_config.host if calling_redis_cfg is None else calling_redis_cfg["host"]
    redis_port = redis_config.port if calling_redis_cfg is None else calling_redis_cfg["port"]
    
    # Connection
    r = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    # Buscar el archivo por file_path y actualizar su status
    file_keys = r.keys("file:*")
    file_found = False
    
    for file_key in file_keys:
        stored_path = r.hget(file_key, "file_path")
        if stored_path and stored_path == path:
            # Actualizar status a 1 (Processing)
            r.hset(file_key, "status", "1")
            context.log.info(f"Updated status to Processing for entity file: {file_key}")
            file_found = True
            break
    
    if not file_found:
        context.log.warning(f"Entity file not found in Redis with path: {path}")


