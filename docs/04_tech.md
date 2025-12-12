# Documento Técnico – SP500 Analytics Pipeline

Este documento describe la arquitectura, los componentes técnicos y el flujo operativo del pipeline de ingeniería de datos desarrollado para **SP500 Analytics**.
Complementa al README general y sirve como referencia técnica para el diseño, implementación y operación del sistema.

---

## Índice

- [1. Introducción](#1-introducción)
- [2. Arquitectura General](#2-arquitectura-general)
- [3. Diagrama de Arquitectura](#3-diagrama-de-arquitectura)
- [4. Componentes del sistema](#4-componentes-del-sistema)
    - [4.1 Orquestación – Apache Airflow](#41-orquestación--apache-airflow)
    - [4.2 Data Lake – S3 / MinIO](#42-data-lake--s3--minio)
    - [4.3 Base de Datos – PostgreSQL / Aurora](#43-base-de-datos--postgresql--aurora)
- [5. Pipeline Detallado](#5-pipeline-detallado)
    - [5.1 Ingesta](#51-ingesta)
    - [5.2 Transformación](#52-transformación)
- [6. Lineamientos de calidad (WIP)](#6-lineamientos-de-calidad-wip)
- [7. Infraestructura](#7-infraestructura)
    - [7.1 Local](#71-local)
    - [7.2 Cloud](#72-cloud)
- [8. Visualización – Streamlit](#8-visualización--streamlit)
- [9. Despliegue y CI/CD](#9-despliegue-y-cicd)
    - [9.1 Variables de entorno (Local)](#91-variables-de-entorno-local)
    - [9.2 Airflow Connections](#92-airflow-connections)
    - [9.3 GitHub Actions – Secrets](#93-github-actions--secrets)
- [10. Repositorio](#10-repositorio)

---

# 1. Introducción

El objetivo del proyecto es capturar, almacenar, transformar y modelar datos del índice S&P 500, permitiendo análisis financieros, métricas derivadas y visualizaciones interactivas.
La solución implementa buenas prácticas modernas:

* Data Lake por capas

* Orquestación con Airflow

* Transformaciones ELT

* Modelado multidimensional (Gold)

* Exposición mediante Streamlit

---

# 2. Arquitectura General

El pipeline se organiza en capas, siguiendo el paradigma Bronze → Silver → Gold:

1. **Bronze (Raw)**:
Datos crudos descargados desde Kaggle u otras APIs, almacenados sin modificaciones.

2. **Silver (Cleansed)**:
Datos limpios, tipados, normalizados y preparados para analítica.

3. **Gold (Semantic Layer)**:
Modelos dimensionales, tablas de hechos y métricas financieras.
Construido completamente con DBT.

4. **Consumo (UI / Notebooks / Dashboards)**:
Visualización y análisis mediante la UI de Streamlit.

---

# 3. Diagrama de Arquitectura

El pipeline sigue el flujo:

Kaggle/API → Airflow → S3/MinIO → PostgreSQL → Gold → Streamlit


Diagrama simplificado (Mermaid):

![Diagrama de Arquitectura](/assets/diagram.svg)
- [`Documento de arquitectura`](/docs/03_project_architecture.md)


# 4. Componentes del sistema

## 4.1 Orquestación – Apache Airflow

Airflow administra la ejecución de:

- Ingesta de archivos CSV/API

- Limpieza y validación

- Cargas a la base de datos

- Transformaciones

Cada DAG está modularizado y dividido en tareas:


| DAG                 | Archivo                                      | Propósito                                                                |
| ------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| **Ingesta Raw API** | `airflow/dags/bronze_kaggle_ingest.py`       | Descarga datasets de kaggle api hacia S3.                                |
| **Ingesta Diaria**  | `airflow/dags/bronze_daily_sp500_ingest.py`  | Consulta diaria del top 10 de simbolos del sp500                         |
| **Bronze → Silver** | `airflow/dags/bronze_process_to_rds.py`      | Limpieza, validación y carga de tablas normalizadas en PostgreSQL.       |
| **Diaria → Silver** | `airflow/dags/silver_daily_sp500_process.py` | Limpieza, validación y carga de tablas normalizadas en Parque    .       |
| **Silver → Gold**   | `airflow/dags/silver_process.py`             | Ejecuta construcción de modelos dimensionales y métricas (capa Gold).    |

## 4.2 Data Lake – S3 / MinIO

Estructura:

s3://henry-sp500-dataset/raw/
s3://henry-sp500-dataset/bronze/
s3://henry-sp500-dataset/silver/
s3://henry-sp500-dataset/gold/


### Propósito de cada capa:

- Bronze =>
     - Datos crudos sin modificaciones.
     - Estructura similar a la fuente.

- Silver => Datos limpios.
        -   Tipos corregidos.
        -   Columnas estandarizadas.
        -   Normalización (por ejemplo, separar tablas de empresas e índices).

- Gold =>
     - Tablas de hechos:

          - fact_daily_prices

          - fact_returns

          - fact_company_metrics

     - Dimensiones:

          - dim_company

          - dim_sector

          - dim_date

     - Métricas derivadas:

          - volatilidad,

          - crecimiento,

          - retornos porcentuales,

          - comparativas multiempresa.

## 4.3 Base de Datos – PostgreSQL / Aurora

Se utiliza PostgreSQL (local) o Aurora PostgreSQL (cloud) como base analítica para:

- Capa Silver (intermedia)

- Capa Gold (materialización desde DBT)

- Integración con UI

Tablas Silver típicas:

- silver_company_info

- silver_historical_prices

- silver_company_reviews

# 5. Pipeline Detallado
## 5.1 Ingesta

### Tecnologías:

- kagglehub
- Peticiones a APIs
- Lectura y validación
- Salida: archivos crudos en Raw/Bronze.

## 5.2 Transformación

- Limpieza de valores faltantes
- Conversión de strings a fechas
- Transformación de tipos numéricos
- Normalización de columnas


## 6. Lineamientos de calidad (WIP)

En una etapa posterior se agregarán:

Tests de datos:

- Unicidad
- No nulos
- Relaciones
Validaciones de esquema:

- Campos obligatorios
- Tipos correctos


## 7. Infraestructura
### 7.1 Local

| Servicio                          | Propósito                  |
| --------------------------------- | -------------------------- |
| **Airflow Webserver / Scheduler** | Orquestación del pipeline  |
| **PostgreSQL**                    | Almacenamiento Silver/Gold |
| **MinIO**                         | Data Lake local            |
| **Streamlit**                     | Visualización              |
| **Airflow Worker / Triggerer**    | Ejecución de tareas        |


## 7.2 Cloud

- S3 para Data Lake real
- Airflow en ECS
- Aurora PostgreSQL
- IAM (least privilege)
- Pipeline CI/CD con GitHub Actions y despliegue autónomo

## 8. Visualización – Streamlit

UI ubicada en
```
/streamlit/app.py
```
Permite:

- Ver precios diarios del S&P 500
- Comparar empresas
- Filtrar por sector, fecha y símbolos
- Graficar retornos y tendencias
- Consultar métricas provenientes de la capa Gold
- Conexión directa a PostgreSQL.

## 9. Despliegue y CI/CD

El proyecto cuenta con un pipeline completo de CI/CD (GitHub Actions):

* Build & Push automático a Docker Hub

     - Airflow ETL

     -   Streamlit UI

* Despliegue automático en EC2

     -   Actualización por SSH

     -   Reinicio controlado de contenedores

     -   Inyección segura de variables (FERNET_KEY, DB creds)

* Logging centralizado

     Todos los servicios escriben en AWS CloudWatch:

     -   Webserver

     -   Scheduler

     -   Triggerer

     -   Streamlit

*   Seguridad

     El pipeline utiliza múltiples credenciales para orquestación, acceso a datos, despliegue cloud y cifrado interno.
     Todas las claves se gestionan siguiendo principios de seguridad:

     -   Nunca se almacenan en el repositorio.

     -   Se gestionan mediante env vars, Airflow Connections y GitHub Secrets.

     -   Se aíslan por entorno (local / cloud).

## 9.1 Variables de entorno (Local)

En desarrollo, se utiliza un archivo .env cargado por Airflow y los scripts del pipeline.

Variables críticas:

| Variable                         | Uso                                                 |
| -------------------------------- | --------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`              | Acceso al bucket S3 / MinIO (modo local usa MinIO). |
| `AWS_SECRET_ACCESS_KEY`          | Acceso al bucket S3.                                |
| `AWS_DEFAULT_REGION`             | Región de los servicios AWS.                        |
| `DB_HOST`                        | Host PostgreSQL local o remoto.                     |
| `DB_USER`                        | Usuario de la base.                                 |
| `DB_PASSWORD`                    | Contraseña.                                         |
| `FERNET_KEY`                     | Cifrado de conexiones Airflow.                      |
| `AIRFLOW__WEBSERVER__SECRET_KEY` | Firmado de sesiones Webserver.                      |

## 9.2 Airflow Connections

Airflow maneja credenciales internas mediante su UI.

Conexiones configuradas:

| Connection ID      | Tipo                | Propósito                                          |
| ------------------ | ------------------- | -------------------------------------------------- |
| `aws_default`      | Amazon Web Services | Acceso a S3, lectura/escritura del Data Lake.      |
| `postgres_default` | Postgres            | Acceso a PostgreSQL/Aurora para capas Silver/Gold. |
| `minio_default`    | S3-like             | Solo entorno local.                                |

Todas están cifradas mediante `FERNET_KEY`.

## 9.3 GitHub Actions – Secrets

Para CI/CD y despliegue del proyecto se usan __GitHub Secrets__:

| Secret                           | Propósito                                                 |
| -------------------------------- | --------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`              | Permite a GitHub Actions desplegar en AWS.                |
| `AWS_SECRET_ACCESS_KEY`          | Acceso a AWS desde el pipeline CI.                        |
| `AWS_DEFAULT_REGION`             | Región de despliegue.                                     |
| `EC2_SSH_KEY`                    | Autenticación para desplegar código en EC2 (si aplica).   |
| `RDS_PASSWORD`                   | Configuración de Aurora/Postgres en cloud.                |
| `FERNET_KEY`                     | Mantener coherencia con el entorno Airflow en producción. |
| `AIRFLOW__WEBSERVER__SECRET_KEY` | Firmado de sesiones en entorno cloud.                     |

Esto permite:

- Despliegues automáticos a S3

- Deploy de contenedores a ECS

- Sync de DAGs a Airflow en cloud

- Creación automática de la infraestructura IaC (si corresponde)

## 10. Repositorio

Código fuente: https://github.com/LucianaCHA/sp500-analytics
