from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.utils.log.logging_mixin import LoggingMixin
from datetime import datetime, timedelta
import os
import importlib.util

SCRIPT_PATH = "/opt/airflow/pipeline/bronze/scripts/script_ingesta_datasets.py"

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


def run_ingest_script(**context):
    log = LoggingMixin().log

    if not os.path.exists(SCRIPT_PATH):
        raise FileNotFoundError(f"Script not found: {SCRIPT_PATH}")

    spec = importlib.util.spec_from_file_location("kaggle_ingest", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    log.info("Executing Kaggle ingest script...")
    module.main()
    log.info("Script completed successfully")


with DAG(
    dag_id="bronze_ingest_kaggle",
    default_args=default_args,
    start_date=datetime(2025, 11, 19),
    schedule=None,
    catchup=False,
    tags=["bronze", "kaggle", "s3"],
) as dag:

    ingest_task = PythonOperator(
        task_id="ingest_kaggle_to_s3",
        python_callable=run_ingest_script,
        provide_context=True,
    )

    trigger_rds = TriggerDagRunOperator(
        task_id="trigger_bronze_process_to_rds",
        trigger_dag_id="bronze_process_to_rds",
        wait_for_completion=False,
    )

    ingest_task >> trigger_rds
