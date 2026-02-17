import os

from dagster import Definitions, load_assets_from_modules, define_asset_job
from dagster_pyspark import PySparkResource
from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig
from dagster_portada_project.assets import boat_fact_ingestion_assets, entity_ingestion_assets
from dagster_portada_project.utilities import data_layer_builder_config_to_dagster_pyspark
from dagster_portada_project.sensors.ingestion_sensors import create_failure_sensor

boat_fact_all_assets = load_assets_from_modules([boat_fact_ingestion_assets], group_name="grup_boat_fact")
entity_all_assets = load_assets_from_modules([entity_ingestion_assets], group_name="grup_entity")

entry_ingestion = define_asset_job(
    name="entry_ingestion",
    selection="group:grup_boat_fact",
    tags={"process": "ingestion"},
)

entity_ingestion = define_asset_job(
    name="entity_ingestion",
    selection="group:grup_entity",
    tags={"process": "ingestion"},
)

cfg_path = os.getenv("DATA_LAYER_CONFIG", "config/delta_data_layer_config.json")
redis_host = os.getenv("REDIS_HOST", "l")
redis_port = os.getenv("REDIS_PORT", "5700")

jobs = [entity_ingestion, entry_ingestion]

redi_cfg = RedisConfig(host=redis_host, port=redis_port)


def callback_error(param, log):
    log.info(f"host: {redi_cfg.host}")
    log.info(f"port: {redi_cfg.port}")
    log.info(f"params: {param}")


ingestion_error_sensor = create_failure_sensor(jobs, "error_sensor", callback_error)

if os.path.exists(cfg_path):
    spark_config = data_layer_builder_config_to_dagster_pyspark(cfg_path)
    py_spark_resource = PySparkResource(spark_config=spark_config)
    defs = Definitions(
        assets=[*boat_fact_all_assets, *entity_all_assets],
        resources={
            "py_spark_resource": py_spark_resource,
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource),
            "redis_config": redi_cfg
        },
        sensors=[ingestion_error_sensor],
        jobs=jobs
    )
else:
    py_spark_resource = PySparkResource(spark_config={
        "spark.master": "local[*]"
    })

    defs = Definitions(
        assets=[*boat_fact_all_assets, *entity_all_assets],
        resources={
            "py_spark_resource": py_spark_resource,
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource),
            "redis_config": RedisConfig({"host": redis_host, "port": redis_port})
        },
        sensors=[ingestion_error_sensor],
        jobs=jobs
    )

# from pathlib import Path
# import dagster as dg
#
# from dagster_portada_project.assets.boat_fact_ingestion_assets import ingestion
# from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource
#
# data_layer = DeltaDataLayerResource()
#
# defs = dg.load_from_defs_folder(project_root=Path(__file__).parent).merge(
#     dg.Definitions(
#         jobs=[ingestion],
#         resources={"datalayer": data_layer}
#     )
# )
