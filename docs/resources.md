# Resources

## Introducción

Los Resources en Dagster son objetos que encapsulan conexiones y configuraciones externas. Se inyectan en los assets y proporcionan acceso a servicios como bases de datos, APIs, o en este caso, Spark y Redis.

## Resources Disponibles

### DeltaDataLayerResource

**Ubicación:** `dagster_portada_project/resources/delta_data_layer_resource.py`

**Descripción:** Resource principal que encapsula la gestión de Apache Spark y Delta Lake para el proyecto Portada.

#### Atributos

```python
class DeltaDataLayerResource(ConfigurableResource):
    config_path: str = ""           # Ruta al archivo de configuración JSON
    job_name: str = ""              # Nombre del job actual
    py_spark_resource: PySparkResource  # Resource de PySpark
```

#### Métodos

##### setup()

Inicializa el layer builder con la configuración del archivo JSON.

```python
def setup(self):
    if not hasattr(self, "_layer_builder"):
        with open(self.config_path) as f:
            config = json.load(f)
        self._layer_builder = DagsterDataLayerBuilder(
            json_config=config, 
            py_spark_resource=self.py_spark_resource
        )
```

##### get_delta_layer()

Retorna una instancia de `DeltaDataLayer` configurada.

```python
def get_delta_layer(self) -> DeltaDataLayer:
    self.setup()
    jn = self.job_name
    return self.layer_builder.build().set_transformer_block(jn)
```

**Uso:**
```python
@asset
def my_asset(datalayer: DeltaDataLayerResource):
    layer = datalayer.get_delta_layer()
    # Usar layer para operaciones genéricas
```

##### get_boat_fact_layer()

Retorna una capa específica para boat facts (noticias).

```python
def get_boat_fact_layer(self):
    self.setup()
    jn = self.job_name
    return self._layer_builder.build(PortadaBuilder.NEWS_TYPE).set_transformer_block(jn)
```

**Uso:**
```python
@asset
def ingested_entry_file(datalayer: DeltaDataLayerResource):
    layer = datalayer.get_boat_fact_layer()
    layer.start_session()
    data, dest_path = layer.copy_ingested_raw_data(
        "ship_entries", 
        local_path=local_path, 
        return_dest_path=True, 
        user=user
    )
```

##### get_know_entities_layer()

Retorna una capa específica para entidades conocidas.

```python
def get_know_entities_layer(self):
    self.setup()
    jn = self.job_name
    return self._layer_builder.build(PortadaBuilder.KNOWN_ENTITIES_TYPE).set_transformer_block(jn)
```

**Uso:**
```python
@asset
def ingested_entity_file(datalayer: DeltaDataLayerResource):
    layer = datalayer.get_know_entities_layer()
    layer.start_session()
    data, dest_path = layer.copy_ingested_raw_data(
        entity_type, 
        local_path=local_path, 
        return_dest_path=True
    )
```

---

### RedisConfig

**Ubicación:** `dagster_portada_project/resources/delta_data_layer_resource.py`

**Descripción:** Resource que encapsula la configuración de conexión a Redis.

#### Atributos

```python
class RedisConfig(ConfigurableResource):
    host: str  # Host del servidor Redis
    port: str  # Puerto del servidor Redis
```

#### Uso en Assets

```python
@asset
def update_data_base_for_entry(
    context: AssetExecutionContext, 
    path, 
    redis_config: RedisConfig
) -> None:
    # Conectar a Redis
    r = redis.Redis(
        host=redis_config.host, 
        port=redis_config.port, 
        decode_responses=True
    )
    
    # Usar conexión
    file_keys = r.keys("file:*")
    # ...
```

---

### PySparkResource

**Origen:** `dagster_pyspark`

**Descripción:** Resource proporcionado por Dagster para gestionar sesiones de Apache Spark.

#### Configuración

```python
from dagster_pyspark import PySparkResource

py_spark_resource = PySparkResource(spark_config={
    "spark.master": "local[*]",
    "spark.app.name": "PortadaDataLayer",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
})
```

#### Uso

El `PySparkResource` se inyecta en `DeltaDataLayerResource` y no se usa directamente en los assets.

---

## Configuración de Resources

### En definitions.py

```python
from dagster import Definitions
from dagster_pyspark import PySparkResource
from dagster_portada_project.resources.delta_data_layer_resource import (
    DeltaDataLayerResource, 
    RedisConfig
)

# Configurar Spark
spark_config = {
    "spark.master": "local[*]",
    "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
    "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
}
py_spark_resource = PySparkResource(spark_config=spark_config)

# Definir resources
defs = Definitions(
    assets=[...],
    resources={
        "py_spark_resource": py_spark_resource,
        "datalayer": DeltaDataLayerResource(py_spark_resource=py_spark_resource),
        "redis_config": RedisConfig(host="localhost", port="6379")
    }
)
```

### Desde Variables de Entorno

```python
import os

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")
cfg_path = os.getenv("DATA_LAYER_CONFIG", "config/delta_data_layer_config.json")

resources = {
    "py_spark_resource": py_spark_resource,
    "datalayer": DeltaDataLayerResource(
        py_spark_resource=py_spark_resource,
        config_path=cfg_path
    ),
    "redis_config": RedisConfig(host=redis_host, port=redis_port)
}
```

---

## Inyección de Dependencias

### En Assets

Los resources se inyectan automáticamente en los assets mediante type hints:

```python
from dagster import asset, AssetExecutionContext
from dagster_portada_project.resources.delta_data_layer_resource import (
    DeltaDataLayerResource, 
    RedisConfig
)

@asset
def my_asset(
    context: AssetExecutionContext,
    datalayer: DeltaDataLayerResource,
    redis_config: RedisConfig
):
    # Usar resources
    layer = datalayer.get_boat_fact_layer()
    r = redis.Redis(host=redis_config.host, port=redis_config.port)
    # ...
```

### Orden de Parámetros

1. `context`: Siempre primero (opcional)
2. Dependencias de assets (con `AssetIn`)
3. Resources (inyectados por tipo)

```python
@asset(ins={"data": AssetIn("previous_asset")})
def my_asset(
    context: AssetExecutionContext,  # 1. Context
    data,                             # 2. Dependencia
    datalayer: DeltaDataLayerResource,  # 3. Resource
    redis_config: RedisConfig         # 4. Otro resource
):
    pass
```

---

## Utilidades

### data_layer_builder_config_to_dagster_pyspark

**Ubicación:** `dagster_portada_project/utilities.py`

**Descripción:** Convierte la configuración del data layer builder al formato esperado por `PySparkResource`.

```python
def data_layer_builder_config_to_dagster_pyspark(config: dict|str):
    if isinstance(config, str):
        with open(config) as f:
            config = json.load(f)

    spark_config = {}
    
    # Procesar configs array
    for item in json.loads(json.dumps(config["configs"])):
        k = next(iter(item))
        spark_config[k] = item[k]
    
    # Procesar propiedades spark.*
    for k in config:
        if k.startswith("spark."):
            spark_config[k] = config[k]
    
    # Mapear master
    if "master" in config:
        spark_config["spark.master"] = config["master"]
    
    # Mapear app_name
    if "app_name" in config:
        spark_config["spark.app.name"] = config["app_name"]
    
    # Configurar HDFS si es necesario
    if "protocol" in config and config["protocol"].startswith("hdfs://"):
        spark_config["spark.hadoop.fs.defaultFS"] = config["protocol"]
        spark_config["spark.hadoop.fs.hdfs.impl"] = "org.apache.hadoop.hdfs.DistributedFileSystem"
    
    return spark_config
```

**Uso:**
```python
from dagster_portada_project.utilities import data_layer_builder_config_to_dagster_pyspark

cfg_path = "config/delta_data_layer_config.json"
spark_config = data_layer_builder_config_to_dagster_pyspark(cfg_path)
py_spark_resource = PySparkResource(spark_config=spark_config)
```

---

## Buenas Prácticas

1. **Configuración Externa**: Usa variables de entorno para configuraciones sensibles
2. **Lazy Initialization**: Los resources se inicializan solo cuando se usan
3. **Type Hints**: Siempre usa type hints para inyección automática
4. **Reutilización**: Los resources son singleton por run
5. **Testing**: Usa mocks para resources en tests

## Testing de Resources

```python
from dagster import build_asset_context
from dagster_portada_project.resources.delta_data_layer_resource import RedisConfig

def test_asset_with_redis():
    # Mock del resource
    redis_config = RedisConfig(host="localhost", port="6379")
    
    # Crear contexto con resource
    context = build_asset_context(resources={"redis_config": redis_config})
    
    # Ejecutar asset
    result = my_asset(context, redis_config)
    
    assert result is not None
```
