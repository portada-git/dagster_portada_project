# dagster_portada_project/resources/delta_data_layer_resource.py
import json
from dagster import ConfigurableResource, InitResourceContext
from portada_data_layer.portada_delta_builder import PortadaBuilder
from portada_data_layer.delta_data_layer import DeltaDataLayer



class DeltaDataLayerResource(ConfigurableResource):
    """Resource that encapsulates Spark and Delta Lake management for Portada Project using Dagster"""
    config_path: str = ""

    def set_config_path(self, config_path: str):
        self.config_path = config_path
        return self

    def setup(self):
        if not hasattr(self, "_layer_builder"):
            with open(self.config_path) as f:
                config = json.load(f)
            # layer_builder = (
            #     DeltaDataLayerBuilder(config)
            # )
            # self.layer_config = layer_builder.built_configuration()
            self._layer_builder = PortadaBuilder(config)

    def get_delta_layer(self) -> DeltaDataLayer:
        self.setup()
        return self.layer_builder.build()
        # self.setup()
        # _delta_data_layer = self.layer_builder.build()
        # _delta_data_layer.start_session()
        # return _delta_data_layer
        # if not hasattr(self, "_delta_data_layer"):
        #     self.setup()
        #     self._delta_data_layer = self.layer_builder.build()
        #     self._delta_data_layer.start_session()
        # return self._delta_data_layer

        # if not self.layer_config:
        #     self.setup()
        # if not self.layer_config.is_initialized():
        #     self.layer_config.start_spark()
        # return DeltaDataLayer(self.layer_config)

    def get_boat_fact_layer(self):
        self.setup()
        return self._layer_builder.build(PortadaBuilder.BOAT_NEWS_TYPE)
        # self.setup()
        # _boat_fact_layer = self._layer_builder.build(PortadaBuilder.BOAT_NEWS_TYPE)
        # _boat_fact_layer.start_session()
        # return _boat_fact_layer
        # if not hasattr(self, "_boat_fact_layer"):
        #     self.setup()
        #     self._boat_fact_layer = self._layer_builder.build(PortadaBuilder.BOAT_NEWS_TYPE)
        #     self._boat_fact_layer.start_session()
        # return self._boat_fact_layer

        # if not self.layer_config:
        #     self.setup()
        # if not self.layer_config.is_initialized():
        #     self.layer_config.start_spark()
        # return BoatFactDataLayer(self.layer_config)

    def get_know_entities_layer(self):
        self.setup()
        return self._layer_builder.build(PortadaBuilder.KNOWN_ENTITIES_TYPE)
        # self.setup()
        # _know_entities_layer = self._layer_builder.build(PortadaBuilder.KNOWN_ENTITIES_TYPE)
        # _know_entities_layer.start_session()
        # return _know_entities_layer
        # if not hasattr(self, "_know_entities_layer"):
        #     self.setup()
        #     self._know_entities_layer = self._layer_builder.build(PortadaBuilder.KNOWN_ENTITIES_TYPE)
        #     self._know_entities_layer.start_session()
        # return self._know_entities_layer

        # if not self.layer_config:
        #     self.setup()
        # if not self.layer_config.is_initialized():
        #     self.layer_config.start_spark()
        # return BoatFactDataLayer(self.layer_config)