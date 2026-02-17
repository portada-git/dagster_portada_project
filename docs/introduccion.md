# Introducción

## ¿Qué es Dagster Portada Project?

Dagster Portada Project es una solución de orquestación de datos construida sobre [Dagster](https://dagster.io/) que facilita la ingesta, procesamiento y almacenamiento de datos de noticias (boat facts) y entidades conocidas en un Data Lake basado en Delta Lake.

## Propósito

El proyecto está diseñado para:

1. **Automatizar la ingesta de datos**: Procesar archivos JSON con información de noticias y entidades
2. **Garantizar la trazabilidad**: Mantener un registro completo del estado de procesamiento en Redis
3. **Facilitar el procesamiento distribuido**: Utilizar Apache Spark para manejar grandes volúmenes de datos
4. **Proporcionar almacenamiento eficiente**: Usar Delta Lake para almacenamiento ACID-compliant
5. **Monitorear fallos**: Detectar y notificar errores en el pipeline automáticamente

## Casos de Uso

- Ingesta de noticias desde múltiples fuentes
- Procesamiento y normalización de entidades conocidas
- Construcción de un Data Lake para análisis posterior
- Seguimiento del estado de archivos procesados
- Monitoreo de la calidad de datos

## Tecnologías Utilizadas

- **Dagster**: Orquestación y gestión de pipelines
- **Apache Spark**: Procesamiento distribuido de datos
- **Delta Lake**: Formato de almacenamiento con capacidades ACID
- **Redis**: Base de datos en memoria para seguimiento de estado
- **Python 3.9+**: Lenguaje de programación principal
- **py_portada_data_layer**: Librería personalizada para gestión de datos

## Versión

Versión actual: **0.0.29**

## Licencia

MIT License
