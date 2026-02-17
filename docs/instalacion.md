# Instalación y Configuración

## Requisitos Previos

- Python 3.9 o superior (hasta 3.13)
- pip (gestor de paquetes de Python)
- Acceso a un servidor Redis
- Apache Spark (gestionado automáticamente por PySpark)
- Git (para instalar dependencias desde repositorios)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <repository-url>
cd dagster_portada_project
```

### 2. Instalar Dependencias

#### Instalación en Modo Desarrollo

```bash
pip install -e ".[dev]"
```

Esto instalará:
- dagster
- dagster-webserver
- dagster-pyspark
- py_portada_data_layer (desde GitHub)
- redis
- pytest

#### Instalación en Modo Producción

```bash
pip install -e .
```

## Configuración

### Variables de Entorno

Crea un archivo `.env` o configura las siguientes variables:

```bash
# Ruta al archivo de configuración de Delta Layer
export DATA_LAYER_CONFIG="config/delta_data_layer_config.json"

# Configuración de Redis
export REDIS_HOST="localhost"
export REDIS_PORT="6379"
```

### Archivo de Configuración Delta Layer

Crea un archivo `config/delta_data_layer_config.json` con la siguiente estructura:

```json
{
  "master": "local[*]",
  "app_name": "PortadaDataLayer",
  "protocol": "file://",
  "configs": [
    {
      "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension"
    },
    {
      "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    }
  ],
  "base_path": "/path/to/data/lake",
  "raw_path": "raw",
  "bronze_path": "bronze",
  "silver_path": "silver",
  "gold_path": "gold"
}
```

#### Configuración para HDFS

Si usas HDFS como almacenamiento:

```json
{
  "master": "spark://master:7077",
  "app_name": "PortadaDataLayer",
  "protocol": "hdfs://namenode:9000",
  "configs": [
    {
      "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension"
    },
    {
      "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    }
  ],
  "base_path": "/portada/data/lake"
}
```

### Configuración de Redis

Asegúrate de que Redis esté ejecutándose:

```bash
# Iniciar Redis (Linux/Mac)
redis-server

# Verificar conexión
redis-cli ping
# Debería responder: PONG
```

## Verificación de la Instalación

### 1. Verificar Dependencias

```bash
python -c "import dagster; print(dagster.__version__)"
python -c "import pyspark; print(pyspark.__version__)"
python -c "import redis; print(redis.__version__)"
```

### 2. Iniciar Dagster UI

```bash
dagster dev
```

Abre tu navegador en http://localhost:3000

### 3. Verificar Assets

En la interfaz de Dagster:
1. Ve a la pestaña "Assets"
2. Deberías ver dos grupos:
   - `grup_boat_fact` (3 assets)
   - `grup_entity` (3 assets)

### 4. Verificar Jobs

En la pestaña "Jobs":
- `entry_ingestion`
- `entity_ingestion`

## Estructura de Directorios

Después de la instalación, tu proyecto debería tener esta estructura:

```
dagster_portada_project/
├── config/
│   └── delta_data_layer_config.json
├── dagster_portada_project/
│   ├── assets/
│   ├── resources/
│   ├── sensors/
│   └── definitions.py
├── dagster_portada_project_tests/
├── docs/
├── .env
├── pyproject.toml
├── setup.py
└── requirements.txt
```

## Solución de Problemas

### Error: "No module named 'portada_data_layer'"

Asegúrate de tener acceso al repositorio de GitHub y ejecuta:

```bash
pip install git+https://github.com/portada-git/py_portada_data_layer
```

### Error: "Cannot connect to Redis"

Verifica que Redis esté ejecutándose:

```bash
redis-cli ping
```

Si no está instalado:

```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis
```

### Error: "Config file not found"

Si no existe el archivo de configuración, Dagster usará una configuración por defecto con Spark en modo local. Para producción, asegúrate de crear el archivo de configuración.

## Próximos Pasos

- Lee la [Guía de Desarrollo](desarrollo.md) para empezar a trabajar con el proyecto
- Consulta la [Documentación de Assets](assets.md) para entender los pipelines
- Revisa la [Arquitectura](arquitectura.md) para comprender el diseño del sistema
