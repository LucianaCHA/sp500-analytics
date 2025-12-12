# Diseño de la Solución
Proyecto: SP500 Analytics

## Índice
- [1. Introducción](#1-introducción)
- [2. Arquitectura General de la Solución](#2-arquitectura-general-de-la-solución)
    - [2.1 Raw (Layer 0)](#21-raw-layer-0)
    - [2.2 Bronze (Layer 1)](#22-bronze-layer-1)
    - [2.3 Silver (Layer 2)](#23-silver-layer-2)
    - [2.4 Gold (Layer 3)](#24-gold-layer-3)
- [3. Fuentes de Datos](#3-fuentes-de-datos)
- [4. Preguntas de Negocio que la Arquitectura Debe Soportar](#4-preguntas-de-negocio-que-la-arquitectura-debe-soportar)
- [5. Herramientas y Tecnologías Seleccionadas](#5-herramientas-y-tecnologías-seleccionadas)
    - [Procesamiento](#procesamiento)
    - [Orquestación](#orquestación)
    - [Almacenamiento](#almacenamiento)
    - [Infraestructura](#infraestructura)
    - [CI/CD](#cicd)
    - [Calidad de Datos](#calidad-de-datos)
- [6. Diseño del Pipeline de Datos](#6-diseño-del-pipeline-de-datos)
    - [6.1 Ingesta Raw](#61-ingesta-raw)
    - [6.2 Transformación Raw a Bronze](#62-transformación-raw-a-bronze)
    - [6.3 Transformación Bronze a Silver](#63-transformación-bronze-a-silver)
- [7. Modelo de Datos (WIP)](#7-modelo-de-datos-wip)
- [8. Decisiones Técnicas y Trade-offs](#8-decisiones-técnicas-y-trade-offs)
    - [8.1 Elección de Data Lake sobre Data Warehouse](#81-elección-de-data-lake-sobre-data-warehouse)
    - [8.2 Uso de PostgreSQL como complemento](#82-uso-de-postgresql-como-complemento)
    - [8.3 Airflow vs. Lambda](#83-airflow-vs-lambda)
- [9. Futuras Extensiones](#9-futuras-extensiones)
- [10. Conclusión](#10-conclusión)

---

## 1. Introducción
Este documento describe el diseño técnico de la plataforma analítica desarrollada para el proyecto SP500 Analytics. Aquí se detallan las decisiones de arquitectura, herramientas seleccionadas, flujo de ingesta, modelado de datos y criterios técnicos que guían la implementación.

La solución actual implementa un pipeline de datos basado en capas Raw → Bronze → Silver, con transformaciones realizadas íntegramente mediante scripts Python, y funcionando sobre infraestructura AWS aprovisionada con Terraform.

---

## 2. Arquitectura General de la Solución
La arquitectura propuesta sigue un enfoque de Data Lake por capas, utilizando Amazon S3 como almacenamiento central. El diseño contempla las siguientes capas:

### 2.1 Raw (Layer 0)
- Almacena los datos exactamente como llegan desde la fuente.
- No se aplican transformaciones.
- Se utiliza para auditoría, reproducibilidad y trazabilidad.

### 2.2 Bronze (Layer 1)
- Datos limpios y normalizados.
- Conversión de tipos, estandarización de columnas, eliminación de filas corruptas o duplicadas.
- Persistidos siguiendo buenas prácticas de particionamiento y compresión.

### 2.3 Silver (Layer 2)
- Datos modelados para analítica.
- Aplicación de transformaciones semánticas.
- Preparación para modelos dimensionales y uso en BI o ML.

### 2.4 Gold (Layer 3)
- Métricas listas para consumo.
- Tablas altamente agregadas.

---

## 3. Fuentes de Datos
Los datasets utilizados provienen de Kaggle y contienen:

- Histórico del índice S&P 500.
- Precios históricos por empresa perteneciente al índice.
- Metadatos adicionales como sectores, empresas y fechas relevantes.

Los archivos son descargados mediante scripts Python, cargados en S3 y posteriormente transformados en las capas Bronze/Silver.

---

## 4. Preguntas de Negocio que la Arquitectura Debe Soportar
La plataforma está diseñada para permitir responder preguntas tales como:

- ¿Cuáles fueron los períodos de mayor crecimiento o caída del índice?
- ¿Qué empresas presentaron crecimiento sostenido en un período dado?
- ¿Cómo afectan los commodities al comportamiento de las empresas del índice?
- ¿Qué patrones indican tendencia alcista o bajista en el índice?
- ¿Qué impacto tuvieron eventos como pandemias, recesiones o conflictos geopolíticos?
- ¿Cuáles fueron las empresas con mayor crecimiento en los últimos años?

Estas preguntas determinan cómo se construyen las tablas Silver y el modelo dimensional futuro.

---

## 5. Herramientas y Tecnologías Seleccionadas

### Procesamiento
- Python (+ Pandas): ingesta, limpieza, normalización y métricas.

### Orquestación
- Airflow, ejecutado dentro de Docker Compose.

### Almacenamiento
- Amazon S3 como Data Lake.
- AWS RDS (PostgreSQL)

### Infraestructura
- Terraform para provisión de:

    - EC2 para Airflow
    - RDS
    - Buckets S3
    - Roles y policies IAM

- Docker para empaquetado.

### CI/CD
- GitHub Actions para:

    - Linting (pre-commit)

    - Test básico

    - Despliegue a EC2 vía SSH

Las credenciales (AWS, EC2 SSH keys, fernet_key de Airflow, etc.) se manejan en:

- GitHub Actions Secrets
- Variables de entorno del workflow

### Calidad de Datos
- Plan a futuro: Great Expectations o Soda.

---

## 6. Diseño del Pipeline de Datos

### 6.1 Ingesta Raw
Pasos principales:
1. Descarga de CSV desde Kaggle.
2. Carga directa en Amazon S3 en la capa Raw.
3. Validación mínima: existencia del archivo, tamaño > 0 bytes, formato esperado.

El proceso es ejecutado mediante Airflow.

### 6.2 Transformación Raw a Bronze
- Limpieza de columnas.
- Conversión de tipos de datos a formatos consistentes.
- Eliminación de filas incompletas o corruptas.
- Compresión y particionamiento (Apache Parquet).

### 6.3 Transformación Bronze a Silver
- Aplicación de lógica semántica.
- Cálculo de métricas por empresa e índice.
- Preparación de tablas fact y dimension.

---

## 7. Modelo de Datos (WIP)
Se trabaja sobre un modelo tipo estrella, con:

### Tablas de hechos:
- Hecho: precios diarios por empresa.
- Hecho: índices diarios del mercado.

### Dimensiones:
- Dimensión empresa.
- Dimensión fecha.
- Dimensión sector industrial.

Este borrador se ajustará tras definir las métricas definitivas del negocio.

---

## 8. Decisiones Técnicas y Trade-offs

### 8.1 Elección de Data Lake sobre Data Warehouse
- Flexibilidad para almacenar datos heterogéneos.
- Bajo costo en comparación con almacenamiento estructurado.

### 8.2 Uso de PostgreSQL como complemento
- Útil para servir datos a Streamlit
- Excelente para hacer joins y consultas rápidas
- Pero no es un DW ni soporta particionamiento avanzado

### 8.3 Airflow vs. Lambda
- Airflow aporta mayor control, logging y mantenibilidad.
- Se descarta Lambda por su complejidad al manejar múltiples DAGs y dependencias.

---

## 9. Futuras Extensiones
- Incorporación de DBT para formalizar capa Silver/Gold.
- Implementación de métricas Gold persistentes.
- Pruebas de calidad de datos (GE/Soda).

---

## 10. Conclusión
La solución actual implementa un pipeline completo Raw → Bronze → Silver, con transformaciones en Python y consumo final vía Streamlit. La arquitectura es modular y escalable.
