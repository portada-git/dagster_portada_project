from dagster import asset, AssetIn, op, AssetExecutionContext
import logging
import redis

from portada_data_layer.portada_ingestion import BoatFactIngestion

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig

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
    return {"source_path": dest_path, "data_json_array": data}


@asset(ins={"data": AssetIn("ingested_entry_file")})
def raw_entries(context: AssetExecutionContext, data, datalayer: DeltaDataLayerResource) -> str:
    """Copia el fitxer al Data Lake (ingesta)"""
    user = context.run_config["ops"]["ingested_entry_file"]["config"]["user"]
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    layer.save_raw_data("ship_entries", data=data, user=user)
    return data["source_path"]


@asset(ins={"path": AssetIn("raw_entries")})
def update_data_base_for_entry(context: AssetExecutionContext, path, redis_config: RedisConfig) -> None:
    calling_redis_cfg = context.run_config["ops"]["ingested_entry_file"]["config"]["redis_config"] if "redis_config" in context.run_config["ops"]["ingested_entry_file"]["config"] else None
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
            context.log.info(f"Updated status to Processing for file: {file_key}")
            file_found = True
            break
    
    if not file_found:
        context.log.warning(f"File not found in Redis with path: {path}")


