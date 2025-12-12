# Arquitectura del Proyecto

## Índice
- [Descripción General](#descripción-general)
- [1. Capa Raw – Ingesta de Datos](#1-capa-raw--ingesta-de-datos)
- [2. Capa Bronze – Carga en RDS](#2-capa-bronze--carga-en-rds)
- [3. Capa Silver – Transformación Intermedia](#3-capa-silver--transformación-intermedia)
- [4. Capa Gold – Transformaciones Analíticas](#4-capa-gold--transformaciones-analíticas)
- [5. Capa de Consumo – Streamlit](#5-capa-de-consumo--streamlit)
- [Anexo — 1. Diagrama en formato Mermaid](#anexo---1-diagrama-en-formato-mermaid)
- [Anexo — 2. Diagrama end to end propuesto en formato Mermaid](#anexo---2-diagrama-end-to-end-propuesto-en-formato-mermaid)

## Descripción General

La arquitectura del proyecto sigue un enfoque moderno de ingeniería de datos basado en capas (Raw → Bronze → Silver → Gold), orquestado por Apache Airflow, almacenado en Amazon S3 y RDS, transformado y consumido mediante Streamlit.

El objetivo es garantizar calidad, trazabilidad y escalabilidad a través de un pipeline robusto desde la ingesta hasta la generación de modelos analíticos.

---

## 1. Capa Raw – Ingesta de Datos

Los datos provienen de dos fuentes principales:

- **Datasets descargados desde Kaggle**, en formato CSV.
- **API diaria del S&P 500**, que obtiene los Top 10 symbols (actualización incremental diaria).

Toda la ingesta es manejada por los DAGs:
```
bronze_kaggle_ingest.py

bronze_daily_sp500_ingest.py
```

Características de esta capa:

- No hay transformaciones
- Se preserva estructura original
- Representa la “fuente de verdad” del pipeline
- Ideal para re-procesar sin perder la integridad histórica

---

## 2. Capa Bronze – Carga en RDS

Un segundo conjunto de DAGs toma los archivos Raw y los deposita en:
```
s3://henry-sp500-dataset/bronze/
```
En paralelo, los datos se cargan en Amazon RDS (PostgreSQL) utilizando loaders Python basados en:

- BaseRawLoader

- RawTableLoader

- RawJsonbLoader

Objetivo de Bronze:

- Replicar fielmente los datos crudos pero en formato tabular SQL
- Estandarizar nombres de archivos / tablas
- Mantener particionado y controlado el volumen
- Servir como base para validaciones posteriores
- Esta capa no realiza transformaciones semánticas; solo adapta la estructura.

---

## 3. Capa Silver – Transformación Intermedia

La capa Silver es construida por los DAGs:

- silver_daily_sp500_process.py

- bronze_process_to_rds.py

Salida en:
```
s3://henry-sp500-dataset/silver/

```

y tablas equivalentes en RDS.

Aquí ya se aplican transformaciones analíticas:

- Limpieza de valores nulos
- Conversión de tipos (fechas, números, categorías)
- Estandarización de columnas
- Deduplicación
- Normalización por entidades (empresa, sector, precios, métricas)

Propósito:

- Dejar los datos consistentes, limpios y listos para el modelado semántico
- Servir como input estable para DBT

---

## 4. Capa Gold – Transformaciones Analíticas

Las transformaciones analíticas avanzadas se hacen directamente en scripts Python, ubicados dentro del pipeline.

Estos scripts generan:

- series temporales agregadas

- cálculos de retornos

- métricas por empresa

- comparaciones sectoriales

- transformaciones listas para visualizar

Estas métricas no se materializan como tabla Gold persistente:
**se calculan on-demand**.

---

## 5. Capa de Consumo – Streamlit

Streamlit consume los datos desde PostgreSQL, especialmente las tablas limpias de Silver y los resultados generados por los scripts.

La app permite:

- Navegar métricas de precios

- Comparar empresas

- Visualizar retornos y tendencias

- Filtrar por símbolo, fecha y sector

- Explorar datos derivados


![Código fuente](/dashboard/streamlit_app/app.py)

La capa de consumo se basa completamente en PostgreSQL y los scripts que generan vistas/métricas listas para visualización.
---

## Anexo — 1. Diagrama en formato Mermaid

![Diagrama de Arquitectura](/assets/diagram.svg)


## Anexo — 2. Diagrama end to end propuesto en formato Mermaid

![Diagrama de Arquitectura](/assets/diagram_e2e.svg)

## Anexo - 3. Diagrama implementado

![Diagrama de Arquitectura Final](/assets/diagram_e2e_final.svg)
