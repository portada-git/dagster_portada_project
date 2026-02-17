# Guía de Desarrollo

## Configuración del Entorno de Desarrollo

### 1. Instalación

```bash
# Clonar repositorio
git clone <repository-url>
cd dagster_portada_project

# Instalar en modo desarrollo
pip install -e ".[dev]"
```

### 2. Estructura del Proyecto

```
dagster_portada_project/
├── dagster_portada_project/
│   ├── __init__.py
│   ├── definitions.py              # Definiciones principales
│   ├── dagster_portada_data_layer.py  # Builder personalizado
│   ├── utilities.py                # Funciones auxiliares
│   ├── assets/                     # Assets del pipeline
│   │   ├── __init__.py
│   │   ├── boat_fact_ingestion_assets.py
│   │   ├── entity_ingestion_assets.py
│   │   ├── boat_fact_cleaning_assets.py
│   │   └── boat_fact_disambiguation_assets.py
│   ├── resources/                  # Resources
│   │   ├── __init__.py
│   │   └── delta_data_layer_resource.py
│   └── sensors/                    # Sensors
│       └── ingestion_sensors.py
├── dagster_portada_project_tests/  # Tests
│   ├── __init__.py
│   ├── main.py
│   └── test_assets.py
├── docs/                           # Documentación
├── config/                         # Archivos de configuración
├── pyproject.toml
├── setup.py
└── requirements.txt
```

---

## Desarrollo de Assets

### Crear un Nuevo Asset

1. **Crear archivo en `assets/`:**

```python
# dagster_portada_project/assets/my_new_assets.py

from dagster import asset, AssetIn, AssetExecutionContext
from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource

@asset
def my_new_asset(
    context: AssetExecutionContext,
    datalayer: DeltaDataLayerResource
):
    """Descripción del asset"""
    context.log.info("Ejecutando my_new_asset")
    
    # Tu lógica aquí
    result = process_data()
    
    return result
```

2. **Registrar en `definitions.py`:**

```python
from dagster_portada_project.assets import my_new_assets

my_assets = load_assets_from_modules([my_new_assets], group_name="my_group")

defs = Definitions(
    assets=[*boat_fact_all_assets, *entity_all_assets, *my_assets],
    # ...
)
```

### Asset con Dependencias

```python
@asset(ins={"input_data": AssetIn("previous_asset")})
def dependent_asset(
    context: AssetExecutionContext,
    input_data,
    datalayer: DeltaDataLayerResource
):
    """Asset que depende de otro"""
    # Usar input_data del asset anterior
    processed = transform(input_data)
    return processed
```

### Asset con Configuración

```python
@asset
def configurable_asset(context: AssetExecutionContext):
    """Asset con configuración personalizada"""
    config = context.run_config["ops"]["configurable_asset"]["config"]
    
    param1 = config["param1"]
    param2 = config.get("param2", "default_value")
    
    # Procesar con parámetros
    result = process(param1, param2)
    return result
```

### Asset con Metadata

```python
from dagster import Output, MetadataValue

@asset
def asset_with_metadata(context: AssetExecutionContext):
    """Asset que registra metadata"""
    data = load_data()
    
    return Output(
        value=data,
        metadata={
            "num_records": MetadataValue.int(len(data)),
            "preview": MetadataValue.md(data.head().to_markdown()),
            "schema": MetadataValue.json({"columns": list(data.columns)})
        }
    )
```

---

## Desarrollo de Resources

### Crear un Nuevo Resource

```python
# dagster_portada_project/resources/my_resource.py

from dagster import ConfigurableResource
import requests

class APIResource(ConfigurableResource):
    """Resource para conectar a una API externa"""
    base_url: str
    api_key: str
    timeout: int = 30
    
    def get(self, endpoint: str):
        """Realizar GET request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, data: dict):
        """Realizar POST request"""
        url = f"{self.base_url}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.post(url, json=data, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()
```

### Registrar Resource

```python
# definitions.py

from dagster_portada_project.resources.my_resource import APIResource

defs = Definitions(
    assets=[...],
    resources={
        "py_spark_resource": py_spark_resource,
        "datalayer": DeltaDataLayerResource(...),
        "redis_config": RedisConfig(...),
        "api": APIResource(
            base_url="https://api.example.com",
            api_key=os.getenv("API_KEY")
        )
    }
)
```

---

## Testing

### Estructura de Tests

```python
# dagster_portada_project_tests/test_my_assets.py

from dagster import build_asset_context, materialize
from dagster_portada_project.assets.my_new_assets import my_new_asset
from dagster_portada_project.resources.delta_data_layer_resource import DeltaDataLayerResource

def test_my_new_asset():
    """Test básico de asset"""
    # Mock del resource
    datalayer = DeltaDataLayerResource(
        config_path="test_config.json",
        py_spark_resource=None
    )
    
    # Crear contexto
    context = build_asset_context(
        resources={"datalayer": datalayer}
    )
    
    # Ejecutar asset
    result = my_new_asset(context, datalayer)
    
    # Assertions
    assert result is not None
    assert len(result) > 0
```

### Test de Asset con Dependencias

```python
def test_dependent_asset():
    """Test de asset con dependencias"""
    from dagster_portada_project.assets.my_new_assets import (
        previous_asset,
        dependent_asset
    )
    
    # Materializar ambos assets
    result = materialize(
        [previous_asset, dependent_asset],
        resources={
            "datalayer": mock_datalayer,
            "redis_config": mock_redis
        }
    )
    
    assert result.success
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Test específico
pytest dagster_portada_project_tests/test_my_assets.py

# Con cobertura
pytest --cov=dagster_portada_project

# Con verbose
pytest -v
```

---

## Debugging

### Logs en Assets

```python
@asset
def my_asset(context: AssetExecutionContext):
    context.log.debug("Mensaje de debug")
    context.log.info("Información general")
    context.log.warning("Advertencia")
    context.log.error("Error")
    
    try:
        risky_operation()
    except Exception as e:
        context.log.error(f"Error en operación: {str(e)}")
        raise
```

### Debugging en Dagster UI

1. Ejecuta el asset/job
2. Ve a la pestaña "Runs"
3. Selecciona el run
4. Revisa logs en tiempo real
5. Inspecciona metadata de assets

### Debugging Local

```python
# Script de prueba local
from dagster import build_asset_context
from dagster_portada_project.assets.boat_fact_ingestion_assets import ingested_entry_file

# Crear contexto mock
context = build_asset_context(
    run_config={
        "ops": {
            "ingested_entry_file": {
                "config": {
                    "local_path": "test_data.json",
                    "user": "test_user"
                }
            }
        }
    }
)

# Ejecutar directamente
result = ingested_entry_file(context, mock_datalayer)
print(result)
```

---

## Buenas Prácticas

### Código

1. **Type Hints:** Usa type hints en todos los parámetros y retornos
2. **Docstrings:** Documenta todos los assets y funciones
3. **Logging:** Usa `context.log` en lugar de `print()`
4. **Error Handling:** Captura y registra errores apropiadamente
5. **Configuración:** Usa `run_config` para parámetros variables

### Assets

1. **Nombres Descriptivos:** Usa nombres claros y descriptivos
2. **Responsabilidad Única:** Cada asset debe hacer una cosa
3. **Idempotencia:** Los assets deben ser idempotentes
4. **Metadata:** Registra metadata útil para debugging
5. **Grupos:** Organiza assets en grupos lógicos

### Resources

1. **Configuración Externa:** Usa variables de entorno
2. **Lazy Loading:** Inicializa conexiones solo cuando se necesiten
3. **Cleanup:** Implementa cleanup de recursos si es necesario
4. **Testing:** Crea mocks para testing

### Testing

1. **Cobertura:** Apunta a >80% de cobertura
2. **Mocks:** Usa mocks para dependencias externas
3. **Datos de Prueba:** Usa datos pequeños y representativos
4. **Assertions:** Verifica comportamiento, no implementación

---

## Workflow de Desarrollo

### 1. Crear Feature Branch

```bash
git checkout -b feature/my-new-feature
```

### 2. Desarrollar

- Escribe código
- Añade tests
- Ejecuta tests localmente
- Verifica en Dagster UI

### 3. Testing

```bash
# Ejecutar tests
pytest

# Verificar linting
flake8 dagster_portada_project

# Verificar tipos (si usas mypy)
mypy dagster_portada_project
```

### 4. Commit y Push

```bash
git add .
git commit -m "feat: añadir nuevo asset para procesamiento X"
git push origin feature/my-new-feature
```

### 5. Pull Request

- Crea PR en GitHub
- Espera revisión
- Merge a main

---

## Comandos Útiles

```bash
# Iniciar Dagster UI
dagster dev

# Iniciar solo el daemon
dagster-daemon run

# Listar assets
dagster asset list

# Listar jobs
dagster job list

# Ejecutar job desde CLI
dagster job execute -j entry_ingestion

# Materializar asset desde CLI
dagster asset materialize -a ingested_entry_file

# Verificar instalación
dagster --version
```

---

## Troubleshooting

### Error: "Asset not found"

Verifica que el asset esté registrado en `definitions.py`:

```python
from dagster import load_assets_from_modules
from dagster_portada_project.assets import my_new_assets

assets = load_assets_from_modules([my_new_assets])
```

### Error: "Resource not configured"

Asegúrate de que el resource esté en el diccionario de resources:

```python
defs = Definitions(
    assets=[...],
    resources={
        "my_resource": MyResource(...)
    }
)
```

### Error: "Config not provided"

Proporciona la configuración necesaria al ejecutar:

```yaml
ops:
  my_asset:
    config:
      required_param: "value"
```

---

## Recursos Adicionales

- [Documentación de Dagster](https://docs.dagster.io/)
- [Dagster University](https://dagster.io/university)
- [Ejemplos de Dagster](https://github.com/dagster-io/dagster/tree/master/examples)
- [py_portada_data_layer](https://github.com/portada-git/py_portada_data_layer)
