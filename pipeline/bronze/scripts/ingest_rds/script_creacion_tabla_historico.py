"""
Ingesta a RDS:
1. Descarga un CSV desde S3 (datasets-kaggle)
2. Lo transforma en formato JSONB fila por fila
3. Lo inserta en una tabla PostgreSQL en RDS

El proceso completo se encapsula en main() para uso con Airflow.
"""

import pandas as pd
import boto3
from io import StringIO
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB
from botocore.exceptions import ClientError
from config import Config


AWS_KEY = "datasets-kaggle/chickenrobot_historical-stocks-of-companies-of-the-sp-and-500/Sp500_historical.csv"
TABLE_NAME = "company_historical_stocks"

AWS_REGION = Config.AWS_DEFAULT_REGION
AWS_BUCKET = Config.S3_BUCKET

DB_USER = Config.AWS_DB_USER
DB_PASSWORD = Config.AWS_DB_PASSWORD
DB_HOST = Config.AWS_DB_HOST
DB_PORT = Config.AWS_DB_PORT
DB_NAME = Config.AWS_DB_NAME


def download_csv_from_s3(bucket: str, key: str, region: str) -> pd.DataFrame:
    """Descarga un archivo CSV desde S3 y lo devuelve como DataFrame."""
    print(f"Descargando archivo desde S3: s3://{bucket}/{key}")

    try:
        s3 = boto3.client("s3", region_name=region)
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_data = response["Body"].read().decode("utf-8")
    except ClientError as e:
        print(f"Error al descargar archivo de S3: {e}")
        raise

    df = pd.read_csv(StringIO(csv_data), low_memory=False)
    print("CSV descargado correctamente. Primeras filas:")
    print(df.head())

    return df


def connect_to_rds() -> any:
    """Crea una conexión SQLAlchemy al RDS PostgreSQL."""
    db_url = Config.AWS_DB_URL
    print(f"Conectando a RDS: {DB_HOST}:{DB_PORT}/{DB_NAME}")

    engine = create_engine(db_url)
    return engine


def insert_jsonb_table(df: pd.DataFrame, table_name: str, engine):
    """Convierte cada fila a JSON y la inserta en una tabla PostgreSQL con JSONB."""
    print("Transformando filas a formato JSONB...")
    df_json = df.apply(lambda row: row.to_dict(), axis=1).to_frame(name="data")

    print(f"Insertando datos en la tabla '{table_name}'...")

    df_json.to_sql(
        table_name, engine, if_exists="replace", index=False, dtype={"data": JSONB}
    )

    print(f"✔ Tabla '{table_name}' creada e importada exitosamente.")


def main():
    print("\n===== INGESTA: company_historical_stocks =====")

    # 1. Descargar CSV desde S3
    df = download_csv_from_s3(AWS_BUCKET, AWS_KEY, AWS_REGION)

    # 2. Conectar a RDS
    engine = connect_to_rds()

    # 3. Insertar en tabla JSONB
    insert_jsonb_table(df, TABLE_NAME, engine)

    print("===== FIN INGESTA company_historical_stocks =====\n")


if __name__ == "__main__":
    main()
