"""
Ingesta a RDS:
1. Descarga un CSV desde S3 (datasets-kaggle)
2. Carga el DataFrame directamente en PostgreSQL
3. Estructurado con main() para ejecución desde Airflow
"""

import pandas as pd
import boto3
from io import StringIO
from dotenv import load_dotenv
from sqlalchemy import create_engine
from botocore.exceptions import ClientError
from config import Config

load_dotenv()

# --- Config específico ---
AWS_KEY = "datasets-kaggle/vaghefi_company-reviews/company_reviews.csv"
TABLE_NAME = "company_reviews"

AWS_REGION = Config.AWS_DEFAULT_REGION
AWS_BUCKET = Config.S3_BUCKET

DB_USER = Config.AWS_DB_USER
DB_PASSWORD = Config.AWS_DB_PASSWORD
DB_HOST = Config.AWS_DB_HOST
DB_PORT = Config.AWS_DB_PORT
DB_NAME = Config.AWS_DB_NAME


def download_csv_from_s3(bucket: str, key: str, region: str) -> pd.DataFrame:
    """Descarga un CSV desde S3 y lo devuelve como DataFrame."""
    print(f"Descargando archivo desde S3: s3://{bucket}/{key}")

    try:
        s3 = boto3.client("s3", region_name=region)
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_data = response["Body"].read().decode("utf-8")
    except ClientError as e:
        print(f"❌ Error al descargar archivo de S3: {e}")
        raise

    df = pd.read_csv(StringIO(csv_data), low_memory=False)
    print("CSV descargado correctamente. Primeras filas:")
    print(df.head())

    return df


def connect_to_rds():
    """Crea una conexión SQLAlchemy al RDS PostgreSQL."""
    db_url = Config.AWS_DB_URL
    print(f"Conectando a RDS: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    return create_engine(db_url)


def insert_table(df: pd.DataFrame, table_name: str, engine):
    """Inserta un DataFrame completo en una tabla PostgreSQL."""
    print(f"Insertando datos en la tabla '{table_name}'...")
    df.to_sql(table_name, engine, if_exists="replace", index=False)
    print(f"✔ Tabla '{table_name}' creada e importada exitosamente.")


def main():
    print("\n===== INGESTA: company_reviews =====")

    # 1. Descargar CSV desde S3
    df = download_csv_from_s3(AWS_BUCKET, AWS_KEY, AWS_REGION)

    # 2. Conectar a RDS
    engine = connect_to_rds()

    # 3. Insertar tabla
    insert_table(df, TABLE_NAME, engine)

    print("===== FIN INGESTA company_reviews =====\n")


if __name__ == "__main__":
    main()
