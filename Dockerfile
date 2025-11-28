FROM apache/airflow:2.8.2-python3.10
LABEL maintainer="lucianachamorro87@gmail.com"

# Airflow usa este usuario
USER airflow

# Para que Airflow vea tus módulos Python de /opt/airflow/pipeline
ENV PYTHONPATH=/opt/airflow/pipeline:$PYTHONPATH

# Instalar dependencias
COPY requirements.txt /requirements.txt
RUN pip install --user --upgrade pip && \
    pip install --user -r /requirements.txt

# Copiar código de negocio (pipeline)
# COPY pipeline/ /opt/pipeline/

# Copiar DAGs (los que hoy tenés en airflow/dags)
# COPY airflow/dags/ /opt/airflow/dags/

# Arrancar Airflow
CMD ["airflow", "standalone"]