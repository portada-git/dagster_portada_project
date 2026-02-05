import json
import platform

from dagster import execute_job, DagsterInstance, materialize
from dagster_portada_project.assets.boat_fact_ingestion_assets import ingested_entry_file, raw_entries, \
    ingestion  # Importa el teu job des de definitions.py
import os
import shutil
from dagster_graphql import DagsterGraphQLClient


if __name__ == "__main__":
    so = platform.system()
    if so == "Darwin":
        json_path_to_copy = "/Users/josepcanellas/Dropbox/feinesJordi/dades/resultats/prova"
        copy_path = "/Users/josepcanellas/tmp/json_data"
        config_path = "/Users/josepcanellas/PycharmProjects/dagster_portada_project/config/delta_data_layer_config.json"
        if os.path.exists(
                os.path.join("/Users/josepcanellas/Dropbox/feinesJordi/implementacio/delta_lake/delta_test/portada_project")):
            shutil.rmtree("/Users/josepcanellas/Dropbox/feinesJordi/implementacio/delta_lake/delta_test/portada_project")

    else:
        json_path_to_copy = "/home/josep/Dropbox/feinesJordi/dades/resultats/prova"
        copy_path = "/home/josep/tmp/json_data"
        config_path = "/home/josep/PycharmProjects/dagster_portada_project/config/delta_data_layer_config.json"
        if os.path.exists(
                os.path.join("/home/josep/Dropbox/feinesJordi/implementacio/delta_lake/delta_test/portada_project")):
            shutil.rmtree("/home/josep/Dropbox/feinesJordi/implementacio/delta_lake/delta_test/portada_project")



    json_name = "results_boatdata.extractor.json"
    os.makedirs(copy_path, exist_ok=True)
    shutil.copy(os.path.join(json_path_to_copy, json_name), os.path.join(copy_path, json_name))
    json_path = os.path.join(copy_path, json_name)
    data_path = "ship_entries"

    if os.path.exists(config_path):
        with open(config_path) as f:
            cfg = json.load(f)
        spark_config = {}
        for item in json.loads(json.dumps(cfg["configs"])):
            k = next(iter(item))
            spark_config[k]=item[k]
        for k in cfg:
            if k.startswith("spark."):
                spark_config[k] = cfg[k]
        if "master" in cfg:
            spark_config["spark.master"] = cfg["master"]
        if "app_name" in cfg:
            spark_config["spark.app.name"] = cfg["app_name"]
        if "protocol" in cfg and cfg["protocol"].startswith("hdfs://"):
            spark_config["spark.hadoop.fs.defaultFS"] = cfg["protocol"]
            spark_config["spark.hadoop.fs.hdfs.impl"] = "org.apache.hadoop.hdfs.DistributedFileSystem"

    client = DagsterGraphQLClient(hostname="localhost", port_number=3000)
    client.submit_job_execution(
        job_name="ingestion",
        run_config={
            "ops": {"ingested_entry_file": {"config": {"local_path": json_path, "user": "jcb"}}},
            "resources": {
                "py_spark_resource":{
                    "config":{
                        "spark_config": spark_config
                    }
                },
                "datalayer": {
                    "config": {
                        "config_path": config_path,
                        "job_name": "ingestion",
                    }
                }
            }
        }
    )

    # # Executa el job amb la configuració que necessitis
    # result = materialize(
    #     assets=[ingested_entry_file],
    #     run_config={
    #         "ops": {
    #             "ingested_entry_file": {
    #                 "config": {
    #                     "local_path":f"{json_path}",
    #                     "user":"jcb"
    #                 }
    #             }
    #         }
    #     }
    # )
    # print(f"Resultat de l'execució: {result}")
