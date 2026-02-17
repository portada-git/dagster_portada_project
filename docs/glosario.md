# Glosario

## Términos de Dagster

### Asset
Conjunto de datos materializado que representa el resultado de una computación. En este proyecto, los assets procesan archivos JSON y los almacenan en Delta Lake.

### Asset Materialization
Proceso de ejecutar la lógica de un asset para producir o actualizar sus datos.

### Asset Group
Colección de assets relacionados que se pueden ejecutar juntos. Ejemplo: `grup_boat_fact`, `grup_entity`.

### Asset Dependency
Relación entre assets donde uno depende del output de otro. Se define usando `AssetIn`.

### Job
Colección de assets que se ejecutan juntos en un orden específico. Define qué materializar y cuándo.

### Resource
Objeto que encapsula conexiones externas (bases de datos, APIs, etc.) y se inyecta en assets. Ejemplos: `DeltaDataLayerResource`, `RedisConfig`.

### Sensor
Proceso que monitorea eventos y puede lanzar runs automáticamente. Ejemplo: `ingestion_error_sensor`.

### Schedule
Definición de cuándo ejecutar un job automáticamente, usando sintaxis cron.

### Run
Ejecución única de un job o materialización de assets.

### Run Config
Configuración proporcionada en tiempo de ejecución para parametrizar la ejecución de assets.

### Context (AssetExecutionContext)
Objeto que proporciona información sobre la ejecución actual, incluyendo logs, configuración y metadata.

### Metadata
Información adicional sobre un asset, como número de registros, tiempo de procesamiento, etc.

### Dagster Daemon
Proceso en segundo plano que ejecuta schedules y sensors.

---

## Términos del Proyecto

### Boat Fact
Noticia o hecho relacionado con el sector marítimo que se ingesta y procesa.

### Entity
Entidad conocida (persona, organización, lugar) relevante para el dominio del proyecto.

### Ingestion
Proceso de leer datos desde archivos locales y copiarlos al Data Lake.

### Raw Data
Datos en su formato original, sin transformaciones, almacenados en la capa raw del Data Lake.

### Data Layer
Capa de abstracción que gestiona el acceso y transformación de datos en Delta Lake.

### Sequencer
Mecanismo en Redis para asignar IDs únicos y secuenciales a los datos.

---

## Términos de Tecnología

### Delta Lake
Formato de almacenamiento open-source que proporciona transacciones ACID sobre data lakes.

### Apache Spark
Framework de procesamiento distribuido de datos usado para operaciones en Delta Lake.

### PySpark
API de Python para Apache Spark.

### Redis
Base de datos en memoria usada para seguimiento de estado de archivos procesados.

### HDFS (Hadoop Distributed File System)
Sistema de archivos distribuido usado opcionalmente como almacenamiento del Data Lake.

### Data Lake
Repositorio centralizado que almacena datos estructurados y no estructurados a cualquier escala.

---

## Términos de Arquitectura de Datos

### Bronze Layer
Capa de datos raw, sin transformaciones.

### Silver Layer
Capa de datos limpiados y validados.

### Gold Layer
Capa de datos agregados y listos para análisis.

### ETL (Extract, Transform, Load)
Proceso de extraer datos de fuentes, transformarlos y cargarlos en un destino.

### ELT (Extract, Load, Transform)
Variante de ETL donde los datos se cargan primero y se transforman después.

### Idempotencia
Propiedad de una operación que produce el mismo resultado sin importar cuántas veces se ejecute.

### ACID
Propiedades de transacciones de base de datos: Atomicity, Consistency, Isolation, Durability.

---

## Estados de Procesamiento (Redis)

### Status 0 - Pending
Archivo registrado pero aún no procesado.

### Status 1 - Processing
Archivo actualmente en procesamiento.

### Status 2 - Completed
Archivo procesado exitosamente.

### Status 3 - Failed
Procesamiento del archivo falló.

---

## Tipos de Entidades

### persons
Personas relevantes en el dominio marítimo.

### organizations
Organizaciones, empresas o instituciones.

### places
Lugares geográficos relevantes.

### ship_entries
Entradas de noticias relacionadas con barcos y navegación.

---

## Configuración

### config_path
Ruta al archivo JSON de configuración del Data Layer.

### local_path
Ruta local al archivo de datos a procesar.

### source_path
Ruta en el Data Lake donde se almacenan los datos.

### base_path
Ruta base del Data Lake.

### protocol
Protocolo de acceso al almacenamiento (file://, hdfs://, s3://, etc.).

---

## Componentes de Spark

### SparkSession
Punto de entrada para funcionalidad de Spark.

### SparkContext
Conexión al cluster de Spark.

### DataFrame
Colección distribuida de datos organizados en columnas nombradas.

### RDD (Resilient Distributed Dataset)
Colección distribuida inmutable de objetos.

---

## Patrones de Diseño

### Dependency Injection
Patrón donde las dependencias se proporcionan externamente en lugar de crearlas internamente.

### Builder Pattern
Patrón para construir objetos complejos paso a paso. Usado en `DagsterDataLayerBuilder`.

### Resource Pattern
Patrón de Dagster para encapsular conexiones externas.

### Sensor Pattern
Patrón para monitorear eventos y reaccionar automáticamente.

---

## Operaciones de Datos

### Materialization
Proceso de ejecutar la lógica de un asset para producir datos.

### Transformation
Modificación de datos de un formato a otro.

### Validation
Verificación de que los datos cumplen con reglas de calidad.

### Aggregation
Combinación de múltiples registros en resúmenes.

### Partitioning
División de datos en segmentos más pequeños para procesamiento eficiente.

---

## Logging y Monitoreo

### Log Level
Severidad de un mensaje de log: DEBUG, INFO, WARNING, ERROR.

### Run Status
Estado de una ejecución: SUCCESS, FAILURE, CANCELED.

### Execution Time
Tiempo que toma ejecutar un asset o job.

### Throughput
Cantidad de datos procesados por unidad de tiempo.

---

## Testing

### Unit Test
Test de una unidad individual de código (función, método).

### Integration Test
Test de la interacción entre múltiples componentes.

### Mock
Objeto simulado que reemplaza una dependencia real en tests.

### Fixture
Datos o configuración predefinidos para tests.

### Assertion
Verificación de que un resultado cumple con lo esperado.

---

## Abreviaciones Comunes

- **DAG**: Directed Acyclic Graph (Grafo Acíclico Dirigido)
- **API**: Application Programming Interface
- **JSON**: JavaScript Object Notation
- **YAML**: YAML Ain't Markup Language
- **CLI**: Command Line Interface
- **UI**: User Interface
- **ID**: Identifier
- **URL**: Uniform Resource Locator
- **HTTP**: Hypertext Transfer Protocol
- **HTTPS**: HTTP Secure
- **SSH**: Secure Shell
- **AWS**: Amazon Web Services
- **S3**: Simple Storage Service (AWS)
- **EC2**: Elastic Compute Cloud (AWS)

---

## Referencias

Para más información sobre términos específicos:

- [Documentación de Dagster](https://docs.dagster.io/)
- [Documentación de Delta Lake](https://docs.delta.io/)
- [Documentación de Apache Spark](https://spark.apache.org/docs/latest/)
- [Documentación de Redis](https://redis.io/documentation)
