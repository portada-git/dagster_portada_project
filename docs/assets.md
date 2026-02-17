# Assets

## Introducción

Los assets en Dagster representan conjuntos de datos materializados. En este proyecto, los assets forman pipelines de ingesta que procesan archivos JSON y los almacenan en Delta Lake.

## Grupos de Assets

### Grupo: grup_boat_fact

Pipeline de ingesta de noticias (boat facts).

### Grupo: grup_entity

Pipeline de ingesta de entidades conocidas.

---

## Boat Fact Ingestion Assets

### ingested_entry_file

**Tipo:** Asset raíz (sin dependencias)

**Descripción:** Lee un archivo JSON local con datos de noticias y lo copia al Data Lake.

**Parámetros de Configuración:**
```python
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": "/path/to/entries.json",
                "user": "username"
            }
        }
    }
}
```

**Retorna:**
```python
{
    "local_path": str,        # Ruta del archivo local
    "source_path": str,       # Ruta en el Data Lake
    "data_json_array": list   # Datos leídos
}
```

**Ejemplo de Uso:**
```python
# En Dagster UI, ejecutar con configuración:
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": "/data/news/2024-01-15.json",
                "user": "data_engineer"
            }
        }
    }
}
```

---

### raw_entries

**Tipo:** Asset derivado

**Dependencias:** `ingested_entry_file`

**Descripción:** Guarda los datos en formato raw en Delta Lake y configura secuenciadores en Redis.

**Parámetros:**
- Hereda `user` de la configuración de `ingested_entry_file`
- Usa `redis_config` del resource

**Retorna:** `str` - Path del archivo local procesado

**Proceso:**
1. Obtiene la capa de datos de boat facts
2. Configura parámetros de secuenciador en Redis
3. Inicia sesión de Spark
4. Guarda datos en formato raw en Delta Lake

---

### update_data_base_for_entry

**Tipo:** Asset derivado

**Dependencias:** `raw_entries`

**Descripción:** Actualiza el estado del archivo en Redis a "Processing" (status=1).

**Parámetros:**
- `path`: Ruta del archivo procesado
- `redis_config`: Configuración de Redis (puede ser sobreescrita)

**Proceso:**
1. Conecta a Redis
2. Busca el archivo por su path
3. Actualiza el campo `status` a "1" (Processing)
4. Registra la operación en logs

**Configuración Opcional de Redis:**
```python
{
    "ops": {
        "ingested_entry_file": {
            "config": {
                "local_path": "/data/news/file.json",
                "user": "user",
                "redis_config": {
                    "host": "custom-redis-host",
                    "port": "6380"
                }
            }
        }
    }
}
```

---

## Entity Ingestion Assets

### ingested_entity_file

**Tipo:** Asset raíz

**Descripción:** Lee un archivo JSON local con datos de entidades y lo copia al Data Lake.

**Parámetros de Configuración:**
```python
{
    "ops": {
        "ingested_entity_file": {
            "config": {
                "local_path": "/path/to/entities.json",
                "entity_type": "persons"  # o "organizations", "places", etc.
            }
        }
    }
}
```

**Tipos de Entidades Soportados:**
- `persons`: Personas
- `organizations`: Organizaciones
- `places`: Lugares
- Otros tipos configurables según el data layer

**Retorna:**
```python
{
    "local_path": str,    # Ruta del archivo local
    "source_path": str,   # Ruta en el Data Lake
    "data": list          # Datos leídos
}
```

---

### raw_entities

**Tipo:** Asset derivado

**Dependencias:** `ingested_entity_file`

**Descripción:** Guarda las entidades en formato raw en Delta Lake.

**Parámetros:**
- Hereda `entity_type` de la configuración de `ingested_entity_file`

**Retorna:** `str` - Path del archivo local procesado

---

### update_data_base_for_entity

**Tipo:** Asset derivado

**Dependencias:** `raw_entities`

**Descripción:** Actualiza el estado del archivo de entidades en Redis a "Processing".

**Funcionamiento:** Similar a `update_data_base_for_entry`, pero para archivos de entidades.

---

## Dependencias entre Assets

### Pipeline Boat Fact

```
ingested_entry_file
        ↓
   raw_entries
        ↓
update_data_base_for_entry
```

### Pipeline Entity

```
ingested_entity_file
        ↓
   raw_entities
        ↓
update_data_base_for_entity
```

## Materialización de Assets

### Desde Dagster UI

1. Navega a la pestaña "Assets"
2. Selecciona el asset que deseas materializar
3. Haz clic en "Materialize"
4. Proporciona la configuración necesaria
5. Haz clic en "Launch Run"

### Desde Python

```python
from dagster import materialize
from dagster_portada_project.assets import boat_fact_ingestion_assets

result = materialize(
    [boat_fact_ingestion_assets],
    run_config={
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": "/data/news.json",
                    "user": "admin"
                }
            }
        }
    }
)
```

## Logs y Monitoreo

Cada asset registra información en los logs de Dagster:

- Número de registros procesados
- Rutas de archivos
- Operaciones en Redis
- Errores y advertencias

Accede a los logs desde:
- Dagster UI → Runs → Selecciona un run → Logs
- Logs de aplicación en `context.log.info()`, `context.log.warning()`, etc.

## Buenas Prácticas

1. **Validación de Datos**: Asegúrate de que los archivos JSON tengan el formato correcto
2. **Gestión de Errores**: Los sensores capturarán fallos automáticamente
3. **Configuración**: Usa variables de entorno para configuraciones sensibles
4. **Testing**: Prueba con archivos pequeños antes de procesar grandes volúmenes
5. **Monitoreo**: Revisa los logs regularmente para detectar problemas
