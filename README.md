# SP500 Analytics Pipeline

Este proyecto implementa un pipeline de datos completo para la captura, procesamiento, modelado y análisis de indicadores del índice S&P500. Su objetivo es ofrecer datos confiables y accesibles para la investigación financiera, educación en inversiones y análisis de mercado.

## Objetivo del proyecto

El propósito del pipeline es obtener datos históricos y actuales del S&P500, procesarlos siguiendo buenas prácticas de ingeniería de datos y disponibilizarlos de manera estructurada para su consumo analítico mediante dashboards, consultas SQL o modelos de análisis.

# Flujo general del pipeline (WIP)

* Ingesta de datos del índice S&P500 desde Kaggle u otra fuente

* Almacenamiento sin procesar en la zona raw

* Transformaciones con PySpark o Pandas

* Generación de datasets limpios y normalizados en la zona clean

* Modelado semántico con DBT en la zona curated

* Exposición a dashboards y consultas analíticas

## Arquitectura técnica

El pipeline está basado en una arquitectura modular basada en los pasos del pipeline, para facilitar la escalabilidad y el mantenimiento.

| Componente            | Tecnología                                   |
| --------------------- | -------------------------------------------- |
| Orquestación          | Apache Airflow                               |
| Ingesta               | Kaggle API / Python                          |
| Almacenamiento bruto  | Amazon S3 (raw zone)                         |
| Procesamiento         | PySpark / Pandas                             |
| Almacenamiento curado | S3 (curated zone)                            |
| Modelado semántico    | DBT                                          |
| Data Warehouse        | Postgres / DuckDB / Redshift (según entorno) |
| Visualización         | PowerBI / Superset / Metabase                |




## Estructura general del proyecto
```
sp500-analytics/
├── airflow/
│ ├── dags/
│ ├── logs/
│ └── plugins/
├── data/ # datos locales para desarrollo/test idealmente no sube a git
│   ├── raw/
│   ├── clean/
│   └── curated/
├── dbt/  # proyecto dbt 
│   └── models/
│       ├── staging/
│       ├── intermediate/
│       └── marts/
├── docs/
│   ├── tecnico.md
│   ├── arquitectura.png
│   ├── modelo_datos.png
│   └── pipeline_diagrama.png
├── minio/
│ └── data/
├── scripts/
├── notebook/               
├── infra/ # config de servicios y docker
├── dashboard/ # tablero
├── tests/
├── .gitignore
├── README.md
└── requirements.txt

```

## Documentación ampliada 
- [`Documento técnico`](docs/tech.md)

## Requisitos

- Python 3.10+

- Docker / Docker Compose

- AWS CLI configurado (cuando se utilice S3 real)

- DBT

- Airflow

## Instalación y uso (versión local de desarrollo)

### **1. Variables de entorno (.env)**

Todas las configuraciones del entorno local se manejan mediante el archivo `.env` en la raíz.

Ejemplo:
```
AWS_ACCESS_KEY_ID=admin
```
### **2. Instalación – Versión local (dev)***

### Levantar todo el entorno

```sh
docker compose -p sp-500 up --build
```
- Esto levanta:

- Airflow Webserver http://localhost:8080
- Airflow Scheduler
- Airflow Worker
- Airflow Triggerer
- Redis (Broker)
- Postgres (Data Warehouse)
- MinIO (Data Lake local)

Accesos
Airflow UI

http://localhost:8080

user: admin

password: admin

MinIO (simula AWS S3)

http://localhost:9001

user: admin

password: admin123

Bucket creado automáticamente:
sp500-bronze