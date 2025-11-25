import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import boto3
import os
from io import StringIO
import logging
from config import Config


def main():
    logging.info("🔄 Iniciando proceso de carga sp500_stocks.csv a RDS...")

    # -----------------------------------------------------
    # Cargar variables desde .env
    # -----------------------------------------------------
    load_dotenv()

    # AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-2")
    # AWS_BUCKET = "henry-sp500-datasets"
    AWS_KEY = "datasets-kaggle/andrewmvd_sp-500-stocks/sp500_stocks.csv"
    TABLE_NAME = "company_stocks"

    AWS_REGION = Config.AWS_DEFAULT_REGION
    AWS_BUCKET = Config.S3_BUCKET

    DB_USER = Config.AWS_DB_USER
    DB_PASSWORD = Config.AWS_DB_PASSWORD
    DB_HOST = Config.AWS_DB_HOST
    DB_PORT = Config.AWS_DB_PORT
    DB_NAME = Config.AWS_DB_NAME

    # -----------------------------------------------------
    # Descargar archivo desde S3
    # -----------------------------------------------------
    logging.info(f"📥 Descargando archivo desde S3: {AWS_KEY}")

    try:
        s3 = boto3.client("s3", region_name=AWS_REGION)
        response = s3.get_object(Bucket=AWS_BUCKET, Key=AWS_KEY)
        csv_data = response["Body"].read().decode("utf-8")
    except Exception as e:
        logging.error(f"❌ Error descargando archivo desde S3: {e}")
        raise

    df = pd.read_csv(StringIO(csv_data))
    logging.info(f"✔ CSV leído. Filas: {len(df)}. Columnas: {len(df.columns)}.")

    # -----------------------------------------------------
    # Conectar a RDS PostgreSQL
    # -----------------------------------------------------
    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    logging.info("🔗 Conectando a la base de datos RDS...")
    try:
        engine = create_engine(db_url)
        conn = engine.connect()
        conn.close()
    except Exception as e:
        logging.error(f"❌ Error conectando a la base de datos RDS: {e}")
        raise

    # -----------------------------------------------------
    # Crear tabla e insertar datos
    # -----------------------------------------------------
    logging.info(f"⬆ Cargando datos en la tabla '{TABLE_NAME}'...")

    try:
        df.to_sql(TABLE_NAME, engine, if_exists="replace", index=False)
        logging.info(f"✔ Tabla '{TABLE_NAME}' creada/actualizada exitosamente.")
    except Exception as e:
        logging.error(f"❌ Error cargando datos en RDS: {e}")
        raise


if __name__ == "__main__":
    main()
