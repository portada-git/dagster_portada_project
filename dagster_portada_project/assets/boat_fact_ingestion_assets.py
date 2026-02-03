from dagster import asset, AssetIn, Config, MetadataValue, AssetExecutionContext, job, define_asset_job
import os, json, logging

from portada_data_layer.portada_ingestion import BoatFactIngestion

from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource

logger = logging.getLogger("boat_fact_dagster")

@asset
def ingested_entry_file(context, datalayer: DeltaDataLayerResource) -> dict:
    """Read local JSON file"""
    local_path = context.run_config["ops"]["ingested_entry_file"]["config"]["local_path"]
    user = context.run_config["ops"]["ingested_entry_file"]["config"]["user"]
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    data, dest_path = layer.copy_ingested_raw_data("ship_entries", local_path=local_path, return_dest_path=True, user=user)
    context.run_config["ops"]["ingested_entry_file"]["config"]["source_path"] = dest_path
    context.log.info(f"Llegits {len(data)} registres de {local_path}")
    return {"source_path": dest_path, "data_json_array": data}

@asset(ins={"data": AssetIn("ingested_entry_file")})
def raw_entries(context: AssetExecutionContext, data, datalayer: DeltaDataLayerResource) -> None:
    """Copia el fitxer al Data Lake (ingesta)"""
    user = context.run_config["ops"]["ingested_entry_file"]["config"]["user"]
    # source_path = context.run_config["ops"]["ingested_entry_file"]["config"]["source_path"]
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    layer.save_raw_data("ship_entries", data=data, user=user)


ingestion = define_asset_job(
    name="ingestion",
    selection="*",
    tags={"process": "ingestion"},
)

# @job()
# def ingestion():
#     ingested_entry_file()
