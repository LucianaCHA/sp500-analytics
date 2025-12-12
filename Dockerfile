FROM apache/airflow:2.8.2-python3.10
LABEL maintainer="lucianachamorro87@gmail.com"

USER root

# 1. Instalar dependencias Python
COPY requirements.txt /requirements.txt
RUN chown airflow:0 /requirements.txt

USER airflow

ENV PYTHONPATH=/opt/airflow/pipeline:$PYTHONPATH

RUN pip install --user --upgrade pip && \
    pip install --user -r /requirements.txt

# 2. Copiar pipeline + dags DENTRO DE AIRFLOW
COPY pipeline/ /opt/airflow/pipeline/
COPY airflow/dags/ /opt/airflow/dags/

# ✅ 3. Copiar Streamlit dashboard dentro de la imagen
COPY dashboard/ /opt/airflow/dashboard/

# No defino CMD acá porque docker-compose / docker run ya pasan el command