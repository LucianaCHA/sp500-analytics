import datetime
from io import BytesIO

import boto3
import pandas as pd
import streamlit as st
from botocore.exceptions import ClientError

from config import Config


s3_client = boto3.client(
    "s3",
    aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
    region_name=Config.AWS_DEFAULT_REGION,
)

bucket_name = Config.AWS_S3_BUCKET_NAME
BASE_PREFIX = f"{Config.AWS_S3_GOLD_BASE_PREFIX}/"   # ej: gold/sp500_daily_prices/
FILENAME = Config.AWS_S3_GOLD_FILENAME               # ej: sp500_gold.parquet


def read_parquet_from_s3(bucket: str, key: str) -> pd.DataFrame:
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    return pd.read_parquet(BytesIO(obj["Body"].read()))


def key_for_date(d: datetime.date) -> str:
    # ej: gold/sp500_daily_prices/2025/12/04/sp500_gold.parquet
    return f"{BASE_PREFIX}{d.strftime('%Y/%m/%d')}/{FILENAME}"


def find_latest_key(bucket: str, prefix: str) -> str:
    paginator = s3_client.get_paginator("list_objects_v2")
    latest = None

    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            k = obj["Key"]
            if k.endswith("/" + FILENAME) or k.endswith(FILENAME):
                if latest is None or k > latest:  # YYYY/MM/DD ordena bien
                    latest = k

    if not latest:
        raise FileNotFoundError(
            f"No se encontraron archivos '{FILENAME}' bajo '{prefix}' en el bucket '{bucket}'."
        )

    return latest


def load_s3_gold(bucket: str) -> tuple[pd.DataFrame, str]:
    today = datetime.datetime.now().date()
    today_key = key_for_date(today)

    try:
        return read_parquet_from_s3(bucket, today_key), today_key
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != "NoSuchKey":
            raise
        latest_key = find_latest_key(bucket, BASE_PREFIX)
        return read_parquet_from_s3(bucket, latest_key), latest_key


# --- UI ---
st.set_page_config(page_title="SP500 Gold", layout="wide")

st.title("Vista Gold desde AWS S3")

if bucket_name == "not_set":
    st.error("❌ Falta configurar la variable de entorno S3_BUCKET")
    st.stop()

try:
    df, used_key = load_s3_gold(bucket_name)
    st.caption(f"Archivo cargado: s3://{bucket_name}/{used_key}")
    st.dataframe(df, use_container_width=True)
except Exception as ex:
    st.error(f"❌ Error cargando datos desde S3: {ex}")
    st.stop()