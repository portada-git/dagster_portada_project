import json


def data_layer_builder_config_to_dagster_pyspark(config: dict|str):
    if isinstance(config, str):
        with open(config) as f:
            config = json.load(f)

    spark_config = {}
    for item in json.loads(json.dumps(config["configs"])):
        k = next(iter(item))
        spark_config[k] = item[k]
    for k in config:
        if k.startswith("spark."):
            spark_config[k] = config[k]
    if "master" in config:
        spark_config["spark.master"] = config["master"]
    if "app_name" in config:
        spark_config["spark.app.name"] = config["app_name"]
    if "protocol" in config and config["protocol"].startswith("hdfs://"):
        spark_config["spark.hadoop.fs.defaultFS"] = config["protocol"]
        spark_config["spark.hadoop.fs.hdfs.impl"] = "org.apache.hadoop.hdfs.DistributedFileSystem"
    return spark_config
