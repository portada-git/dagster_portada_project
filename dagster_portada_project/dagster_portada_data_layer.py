import json

from dagster_pyspark import PySparkResource
from portada_data_layer import PortadaBuilder, DeltaDataLayer
from portada_data_layer.portada_ingestion import NewsExtractionIngestion, BoatFactIngestion, KnownEntitiesIngestion


class DagsterDataLayerBuilder(PortadaBuilder):
    def __init__(self, json_config=None, json_extended_classes=None,py_spark_resource: PySparkResource = None):
        super().__init__(json_config, json_extended_classes)
        self._py_spark_resource = py_spark_resource

    def py_spark_resource(self, py_spark_resource: PySparkResource):
        self._py_spark_resource = py_spark_resource
        return self

    def get_spark_builder(self):
        # return self.py_spark_resource.get_spark_clean_builder()
        return None

    def build(self, type:str = None, *args, **kwargs) -> "PortadaIngestion":
        """Constructs and returns a DeltaDataLayer initialized with this constructor."""
        if not type or type == self.DELTA_DATA_LAYER:
            delta_layer = DeltaDataLayer(builder=self)
        elif type == self.NEWS_TYPE:
            delta_layer = NewsExtractionIngestion(builder=self)
        elif type == self.BOAT_NEWS_TYPE:
            delta_layer = BoatFactIngestion(builder=self)
        elif type == self.KNOWN_ENTITIES_TYPE:
            delta_layer = KnownEntitiesIngestion(builder=self)
        elif type in self.CLASS_REGISTRY:
            cls = self.CLASS_REGISTRY[type]
            delta_layer = cls(builder=self)
        else:
            raise Exception(f"Unknown type {type}")
        delta_layer.spark = self._py_spark_resource.spark_session
        return delta_layer



