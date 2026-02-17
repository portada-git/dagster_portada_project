# Arquitectura

## Visión General

El proyecto sigue una arquitectura basada en pipelines de Dagster, donde cada pipeline está compuesto por assets que representan transformaciones de datos.

```
┌─────────────────────────────────────────────────────────────┐
│                    Dagster Orchestration                     │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Boat Fact       │         │  Entity          │          │
│  │  Ingestion       │         │  Ingestion       │          │
│  │  Pipeline        │         │  Pipeline        │          │
│  └──────────────────┘         └──────────────────┘          │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌─────────────────────────────────────────────┐            │
│  │         Delta Data Layer Resource           │            │
│  └─────────────────────────────────────────────┘            │
│           │                            │                     │
│           ▼                            ▼                     │
│  ┌──────────────┐            ┌──────────────┐               │
│  │ Apache Spark │            │    Redis     │               │
│  └──────────────┘            └──────────────┘               │
│           │                                                  │
│           ▼                                                  │
│  ┌──────────────────────────────────────────┐               │
│  │          Delta Lake Storage              │               │
│  └──────────────────────────────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

## Componentes Principales

### 1. Assets

Los assets son las unidades fundamentales de datos en Dagster. Cada asset representa un conjunto de datos materializado.

#### Boat Fact Ingestion Assets
- `ingested_entry_file`: Lee archivos JSON locales de noticias
- `raw_entries`: Guarda datos en formato raw en Delta Lake
- `update_data_base_for_entry`: Actualiza el estado en Redis

#### Entity Ingestion Assets
- `ingested_entity_file`: Lee archivos JSON de entidades
- `raw_entities`: Guarda entidades en Delta Lake
- `update_data_base_for_entity`: Actualiza el estado en Redis

### 2. Resources

#### DeltaDataLayerResource
Resource principal que encapsula la gestión de Spark y Delta Lake.

**Responsabilidades:**
- Inicializar sesiones de Spark
- Gestionar configuración de Delta Lake
- Proporcionar acceso a diferentes capas de datos (boat facts, entidades)

#### RedisConfig
Configuración para conexión a Redis.

**Parámetros:**
- `host`: Host del servidor Redis
- `port`: Puerto del servidor Redis

#### PySparkResource
Resource de Dagster para gestionar sesiones de Spark.

### 3. Jobs

#### entry_ingestion
Job que ejecuta el pipeline completo de ingesta de noticias.

**Selección:** `group:grup_boat_fact`
**Tags:** `{"process": "ingestion"}`

#### entity_ingestion
Job que ejecuta el pipeline completo de ingesta de entidades.

**Selección:** `group:grup_entity`
**Tags:** `{"process": "ingestion"}`

### 4. Sensors

#### ingestion_error_sensor
Sensor que monitorea fallos en los jobs de ingesta.

**Funcionalidad:**
- Detecta fallos en assets
- Recupera configuración del run
- Captura mensajes de error
- Prepara notificaciones (estructura para Slack)

## Flujo de Datos

### Pipeline de Ingesta de Noticias

1. **Lectura de Archivo** (`ingested_entry_file`)
   - Lee archivo JSON local
   - Copia datos al Data Lake
   - Retorna metadata del archivo

2. **Guardado Raw** (`raw_entries`)
   - Recibe datos del paso anterior
   - Guarda en formato raw en Delta Lake
   - Asigna secuenciadores usando Redis
   - Retorna path del archivo

3. **Actualización de Estado** (`update_data_base_for_entry`)
   - Busca el archivo en Redis
   - Actualiza status a "Processing" (1)
   - Registra operación en logs

### Pipeline de Ingesta de Entidades

Similar al pipeline de noticias, pero adaptado para diferentes tipos de entidades:
- Personas
- Organizaciones
- Lugares
- Otros tipos configurables

## Configuración

### Variables de Entorno

```bash
DATA_LAYER_CONFIG=config/delta_data_layer_config.json
REDIS_HOST=localhost
REDIS_PORT=6379
```

### Archivo de Configuración Delta Layer

El archivo JSON de configuración debe incluir:
- Configuración de Spark (`configs`, `master`, `app_name`)
- Protocolo de almacenamiento (`protocol`)
- Configuraciones específicas de Delta Lake

## Patrones de Diseño

### Resource Pattern
Los resources encapsulan dependencias externas (Spark, Redis) y se inyectan en los assets.

### Asset Dependency Pattern
Los assets declaran dependencias explícitas usando `AssetIn`, creando un DAG claro.

### Configuration Pattern
La configuración se pasa mediante `run_config` en tiempo de ejecución, permitiendo flexibilidad.

### Error Handling Pattern
Los sensores monitorizan fallos y permiten implementar estrategias de recuperación.
