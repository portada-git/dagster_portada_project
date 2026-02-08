import os

from dagster import Definitions, load_assets_from_modules
from dagster_pyspark import PySparkResource
from dagster_portada_project.assets.boat_fact_ingestion_assets import ingestion
from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource, RedisConfig
from dagster_portada_project.assets import boat_fact_ingestion_assets
from dagster_portada_project.utilities import data_layer_builder_config_to_dagster_pyspark

all_assets = load_assets_from_modules([boat_fact_ingestion_assets])

cfg_path = os.getenv("DATA_LAYER_CONFIG", "config/delta_data_layer_config.json")
redis_host = os.getenv("REDIS_HOST", "l")
redis_port = os.getenv("REDIS_PORT", "5700")

if os.path.exists(cfg_path):
    spark_config = data_layer_builder_config_to_dagster_pyspark(cfg_path)
    py_spark_resource = PySparkResource(spark_config=spark_config)
    defs = Definitions(
        assets=all_assets,
        resources={
            "py_spark_resource": py_spark_resource,
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource),
            "redis_config": RedisConfig(host=redis_host, port=redis_port)
        },
        jobs=[ingestion]
    )
else:
    py_spark_resource = PySparkResource(spark_config={
        "spark.master": "local[*]"
    })

    defs = Definitions(
        assets=all_assets,
        resources={
            "py_spark_resource": py_spark_resource,
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource),
            "redis_config": RedisConfig({"host": redis_host, "port": redis_port})
        },
        jobs=[ingestion]
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
