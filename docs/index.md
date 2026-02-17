# Documentación Dagster Portada Project

## Índice

1. [Introducción](introduccion.md)
2. [Arquitectura](arquitectura.md)
3. [Instalación y Configuración](instalacion.md)
4. [Assets](assets.md)
5. [Resources](resources.md)
6. [Jobs y Sensors](jobs-sensors.md)
7. [Guía de Desarrollo](desarrollo.md)
8. [API Reference](api-reference.md)
9. [Ejemplos Prácticos](ejemplos.md)
10. [Glosario](glosario.md)
11. [Troubleshooting: Sensores](troubleshooting-sensores.md)

## Descripción General

Dagster Portada Project es un pipeline de ingesta y procesamiento de datos construido con Dagster, diseñado para gestionar la ingesta de noticias (boat facts) y entidades conocidas utilizando Apache Spark y Delta Lake.

## Características Principales

- **Ingesta de Datos**: Pipeline automatizado para procesar archivos JSON de noticias y entidades
- **Integración con Delta Lake**: Almacenamiento eficiente usando formato Delta
- **Apache Spark**: Procesamiento distribuido de datos
- **Redis**: Sistema de seguimiento de estado de archivos procesados
- **Sensores de Fallos**: Monitoreo automático de errores en el pipeline
- **Configuración Flexible**: Soporte para múltiples entornos mediante variables de entorno

## Componentes Principales

- **Assets**: Definición de datos y transformaciones
- **Resources**: Gestión de conexiones a Spark, Delta Lake y Redis
- **Jobs**: Orquestación de pipelines de ingesta
- **Sensors**: Monitoreo y alertas de fallos

## Inicio Rápido

```bash
# Instalar dependencias
pip install -e ".[dev]"

# Iniciar Dagster UI
dagster dev
```

Visita http://localhost:3000 para acceder a la interfaz web.
