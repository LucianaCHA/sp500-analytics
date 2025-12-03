"""Airflow DAG to ingest daily SP500 and SPY raw data into S3 Bronze."""

from datetime import datetime, timedelta

from airflow.operators.python import PythonOperator
from scripts_loader import ScriptLoader

from airflow import DAG

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

SP500_SCRIPT_PATH = (
    "/opt/airflow/pipeline/bronze/scripts/ingest_sp500/sp500_raw_loader.py"
)
SPY_SCRIPT_PATH = (
    "/opt/airflow/pipeline/bronze/scripts/ingest_sp500/spy_holdings_raw_loader.py"
)


def load_sp500_raw(**context):
    """Load the raw SP500 data into S3 Bronze."""
    loader = ScriptLoader(SP500_SCRIPT_PATH)
    loader.load_and_run()


def load_spy_top10_raw(**context):
    """Load the raw SPY Top 10 Holdings data into S3 Bronze."""
    loader = ScriptLoader(SPY_SCRIPT_PATH)
    loader.load_and_run()


with DAG(
    "bronze_daily_sp500_ingest",
    default_args=default_args,
    description="DAG para descargar y cargar archivos RAW (SP500, SPY) a S3",
    schedule_interval="0 15 * * *",
    start_date=datetime(2025, 12, 3),
    catchup=False,
    tags=["bronze", "raw", "s3"],
) as dag:
    load_sp500_task = PythonOperator(
        task_id="load_sp500_raw",
        python_callable=load_sp500_raw,
        provide_context=True,
        dag=dag,
    )

    load_spy_task = PythonOperator(
        task_id="load_spy_top10_raw",
        python_callable=load_spy_top10_raw,
        provide_context=True,
        dag=dag,
    )

    load_sp500_task >> load_spy_task
