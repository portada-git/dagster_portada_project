import json
import os

from dagster import Definitions, load_assets_from_modules
from dagster_pyspark import PySparkResource
from dagster_portada_project.assets.boat_fact_ingestion_assets import ingestion
from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource
from dagster_portada_project.assets import boat_fact_ingestion_assets

all_assets = load_assets_from_modules([boat_fact_ingestion_assets])

cfg_path = os.getenv("DATA_LAYER_CONFIG", "config/delta_data_layer_config.json")
if os.path.exists(cfg_path):
    with open(cfg_path) as f:
        cfg = json.load(f)

    spark_config = {"spark.master": cfg.get("master", "local[*]")}
    for item in cfg["configs"]:
        k = next(iter(item))
        spark_config[k] = item[k]
    for k in cfg:
        if k.startswith("spark."):
            spark_config[k] = cfg[k]
    if "protocol" in cfg and cfg["protocol"].startswith("hdfs://"):
        spark_config["spark.hadoop.fs.defaultFS"] = cfg["protocol"]
        spark_config["spark.hadoop.fs.hdfs.impl"] = "org.apache.hadoop.hdfs.DistributedFileSystem"
    print(spark_config)
    py_spark_resource = PySparkResource(spark_config=spark_config)
    defs = Definitions(
        assets=all_assets,
        resources={
            "py_spark_resource": py_spark_resource,
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource)
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
            "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource)
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
