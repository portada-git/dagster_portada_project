# API Reference

## Assets

### boat_fact_ingestion_assets

#### ingested_entry_file

```python
@asset
def ingested_entry_file(
    context: AssetExecutionContext,
    datalayer: DeltaDataLayerResource
) -> dict
```

Lee un archivo JSON local con datos de noticias y lo copia al Data Lake.

**Parámetros:**
- `context`: Contexto de ejecución de Dagster
- `datalayer`: Resource de Delta Data Layer

**Configuración Requerida:**
```python
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": str,  # Ruta al archivo JSON local
                "user": str         # Usuario que ejecuta la ingesta
            }
        }
    }
}
```

**Retorna:**
```python
{
    "local_path": str,           # Ruta del archivo local
    "source_path": str,          # Ruta en el Data Lake
    "data_json_array": list      # Datos leídos del archivo
}
```

**Ejemplo:**
```python
result = {
    "local_path": "/data/news/2024-01-15.json",
    "source_path": "hdfs://namenode:9000/portada/raw/ship_entries/2024-01-15.json",
    "data_json_array": [{"id": 1, "title": "News 1"}, ...]
}
```

---

#### raw_entries

```python
@asset(ins={"data": AssetIn("ingested_entry_file")})
def raw_entries(
    context: AssetExecutionContext,
    data: dict,
    datalayer: DeltaDataLayerResource,
    redis_config: RedisConfig
) -> str
```

Guarda los datos en formato raw en Delta Lake y configura secuenciadores en Redis.

**Parámetros:**
- `context`: Contexto de ejecución
- `data`: Datos del asset `ingested_entry_file`
- `datalayer`: Resource de Delta Data Layer
- `redis_config`: Configuración de Redis

**Retorna:** `str` - Path del archivo local procesado

---

#### update_data_base_for_entry

```python
@asset(ins={"path": AssetIn("raw_entries")})
def update_data_base_for_entry(
    context: AssetExecutionContext,
    path: str,
    redis_config: RedisConfig
) -> None
```

Actualiza el estado del archivo en Redis a "Processing" (status=1).

**Parámetros:**
- `context`: Contexto de ejecución
- `path`: Ruta del archivo procesado
- `redis_config`: Configuración de Redis

**Configuración Opcional:**
```python
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": str,
                "user": str,
                "redis_config": {
                    "host": str,
                    "port": str
                }
            }
        }
    }
}
```

---

### entity_ingestion_assets

#### ingested_entity_file

```python
@asset
def ingested_entity_file(
    context: AssetExecutionContext,
    datalayer: DeltaDataLayerResource
) -> dict
```

Lee un archivo JSON local con datos de entidades y lo copia al Data Lake.

**Configuración Requerida:**
```python
{
    "ops": {
        "ingested_entity_file": {
            "config": {
                "local_path": str,      # Ruta al archivo JSON
                "entity_type": str      # Tipo de entidad: "persons", "organizations", etc.
            }
        }
    }
}
```

**Retorna:**
```python
{
    "local_path": str,
    "source_path": str,
    "data": list
}
```

---

#### raw_entities

```python
@asset(ins={"data": AssetIn("ingested_entity_file")})
def raw_entities(
    context: AssetExecutionContext,
    data: dict,
    datalayer: DeltaDataLayerResource
) -> str
```

Guarda las entidades en formato raw en Delta Lake.

---

#### update_data_base_for_entity

```python
@asset(ins={"path": AssetIn("raw_entities")})
def update_data_base_for_entity(
    context: AssetExecutionContext,
    path: str,
    redis_config: RedisConfig
) -> None
```

Actualiza el estado del archivo de entidades en Redis.

---

## Resources

### DeltaDataLayerResource

```python
class DeltaDataLayerResource(ConfigurableResource):
    config_path: str = ""
    job_name: str = ""
    py_spark_resource: PySparkResource
```

Resource que encapsula la gestión de Spark y Delta Lake.

#### Métodos

##### setup()

```python
def setup(self) -> None
```

Inicializa el layer builder con la configuración del archivo JSON.

---

##### get_delta_layer()

```python
def get_delta_layer(self) -> DeltaDataLayer
```

Retorna una instancia de `DeltaDataLayer` configurada.

**Retorna:** `DeltaDataLayer`

---

##### get_boat_fact_layer()

```python
def get_boat_fact_layer(self) -> BoatFactIngestion
```

Retorna una capa específica para boat facts (noticias).

**Retorna:** `BoatFactIngestion`

---

##### get_know_entities_layer()

```python
def get_know_entities_layer(self) -> KnownEntitiesLayer
```

Retorna una capa específica para entidades conocidas.

**Retorna:** `KnownEntitiesLayer`

---

### RedisConfig

```python
class RedisConfig(ConfigurableResource):
    host: str
    port: str
```

Resource para configuración de conexión a Redis.

**Atributos:**
- `host`: Host del servidor Redis
- `port`: Puerto del servidor Redis

---

## Utilities

### data_layer_builder_config_to_dagster_pyspark

```python
def data_layer_builder_config_to_dagster_pyspark(
    config: dict | str
) -> dict
```

Convierte la configuración del data layer builder al formato de PySparkResource.

**Parámetros:**
- `config`: Diccionario de configuración o ruta a archivo JSON

**Retorna:** `dict` - Configuración de Spark

**Ejemplo:**
```python
config = {
    "master": "local[*]",
    "app_name": "MyApp",
    "protocol": "hdfs://namenode:9000",
    "configs": [
        {"spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension"}
    ]
}

spark_config = data_layer_builder_config_to_dagster_pyspark(config)
# Resultado:
# {
#     "spark.master": "local[*]",
#     "spark.app.name": "MyApp",
#     "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
#     "spark.hadoop.fs.defaultFS": "hdfs://namenode:9000",
#     "spark.hadoop.fs.hdfs.impl": "org.apache.hadoop.hdfs.DistributedFileSystem"
# }
```

---

## Sensors

### create_failure_sensor

```python
def create_failure_sensor(
    job_list: list,
    sensor_name: str
) -> RunFailureSensorDefinition
```

Crea un sensor que monitorea fallos en jobs.

**Parámetros:**
- `job_list`: Lista de jobs a monitorear
- `sensor_name`: Nombre del sensor

**Retorna:** `RunFailureSensorDefinition`

**Ejemplo:**
```python
jobs = [entry_ingestion, entity_ingestion]
sensor = create_failure_sensor(jobs, "error_sensor")
```

---

### ingestion_error_sensor

```python
@run_failure_sensor(monitored_jobs=job_list, name=sensor_name)
def ingestion_error_sensor(context: RunFailureSensorContext) -> None
```

Sensor que captura fallos en jobs de ingesta.

**Contexto Disponible:**
- `context.dagster_run.run_config`: Configuración del run
- `context.failure_event.step_key`: Asset que falló
- `context.failure_event.message`: Mensaje de error
- `context.instance.get_records_for_run()`: Registros de materializaciones

---

## Jobs

### entry_ingestion

```python
entry_ingestion = define_asset_job(
    name="entry_ingestion",
    selection="group:grup_boat_fact",
    tags={"process": "ingestion"}
)
```

Job que ejecuta el pipeline de ingesta de noticias.

**Assets:** `ingested_entry_file`, `raw_entries`, `update_data_base_for_entry`

**Tags:** `{"process": "ingestion"}`

---

### entity_ingestion

```python
entity_ingestion = define_asset_job(
    name="entity_ingestion",
    selection="group:grup_entity",
    tags={"process": "ingestion"}
)
```

Job que ejecuta el pipeline de ingesta de entidades.

**Assets:** `ingested_entity_file`, `raw_entities`, `update_data_base_for_entity`

**Tags:** `{"process": "ingestion"}`

---

## Data Layer Builder

### DagsterDataLayerBuilder

```python
class DagsterDataLayerBuilder:
    def __init__(
        self,
        json_config: dict = None,
        json_extended_classes: dict = None,
        py_spark_resource: PySparkResource = None
    )
```

Builder personalizado para integrar Portada Data Layer con Dagster.

#### Métodos

##### py_spark_resource

```python
def py_spark_resource(self, py_spark_resource: PySparkResource) -> Self
```

Configura el resource de PySpark.

---

##### get_spark_builder

```python
def get_spark_builder(self) -> SparkBuilder
```

Retorna el builder de Spark configurado.

---

##### build

```python
def build(
    self,
    type: str = None,
    *args,
    **kwargs
) -> PortadaIngestion
```

Construye una instancia de PortadaIngestion.

**Parámetros:**
- `type`: Tipo de ingesta (ej: `PortadaBuilder.NEWS_TYPE`, `PortadaBuilder.KNOWN_ENTITIES_TYPE`)
- `*args`, `**kwargs`: Argumentos adicionales

**Retorna:** `PortadaIngestion`

---

## Tipos y Constantes

### PortadaBuilder Types

```python
PortadaBuilder.NEWS_TYPE           # Para boat facts
PortadaBuilder.KNOWN_ENTITIES_TYPE # Para entidades conocidas
```

### Redis Status Codes

```python
"0"  # Pending
"1"  # Processing
"2"  # Completed
"3"  # Failed
```

---

## Excepciones

Las excepciones son manejadas por Dagster y registradas en los logs. Los sensores capturan fallos automáticamente.

**Excepciones Comunes:**
- `FileNotFoundError`: Archivo de configuración o datos no encontrado
- `redis.ConnectionError`: Error al conectar a Redis
- `pyspark.sql.utils.AnalysisException`: Error en operaciones de Spark
- `json.JSONDecodeError`: Error al parsear JSON

---

## Variables de Entorno

```python
DATA_LAYER_CONFIG: str  # Ruta al archivo de configuración
REDIS_HOST: str         # Host de Redis (default: "localhost")
REDIS_PORT: str         # Puerto de Redis (default: "6379")
```

---

## Configuración de Ejemplo Completa

```python
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": "/data/news/2024-01-15.json",
                "user": "data_engineer",
                "redis_config": {
                    "host": "redis.example.com",
                    "port": "6379"
                }
            }
        }
    },
    "resources": {
        "datalayer": {
            "config": {
                "config_path": "config/delta_data_layer_config.json",
                "job_name": "entry_ingestion"
            }
        }
    }
}
```
