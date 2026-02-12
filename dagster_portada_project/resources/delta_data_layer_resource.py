# dagster_portada_project/resources/delta_data_layer_resource.py
import json
from dagster import ConfigurableResource
from dagster_pyspark import PySparkResource
from portada_data_layer.portada_delta_builder import PortadaBuilder
from portada_data_layer.delta_data_layer import DeltaDataLayer
import redis
from dagster_portada_project.dagster_portada_data_layer import DagsterDataLayerBuilder


class RedisConfig(ConfigurableResource):
    host: str
    port: str


class DeltaDataLayerResource(ConfigurableResource):
    """Resource that encapsulates Spark and Delta Lake management for Portada Project using Dagster"""
    config_path: str = ""
    job_name: str = ""
    py_spark_resource: PySparkResource

    def set_config_path(self, config_path: str):
        self.config_path = config_path
        return self

    def setup(self):
        if not hasattr(self, "_layer_builder"):
            with open(self.config_path) as f:
                config = json.load(f)
            self._layer_builder = DagsterDataLayerBuilder(json_config=config, py_spark_resource=self.py_spark_resource)

    def get_delta_layer(self) -> DeltaDataLayer:
        self.setup()
        jn = self.job_name
        return self.layer_builder.build().set_transformer_block(jn)

    def get_boat_fact_layer(self):
        self.setup()
        jn = self.job_name
        return self._layer_builder.build(PortadaBuilder.NEWS_TYPE).set_transformer_block(jn)

    def get_know_entities_layer(self):
        self.setup()
        jn = self.job_name
        return self._layer_builder.build(PortadaBuilder.KNOWN_ENTITIES_TYPE).set_transformer_block(jn)
