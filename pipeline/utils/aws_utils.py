"""AWS S3 Utility Functions."""

import logging
from io import StringIO

import boto3
import pandas as pd
from botocore.exceptions import ClientError
from config import Config


def download_csv_from_s3(bucket: str, key: str, region: str) -> pd.DataFrame:
    """Download a CSV file from S3 and returns it as a DataFrame."""
    logging.info(f"Downloading file from S3: s3://{bucket}/{key}")
    try:
        s3 = boto3.client("s3", region_name=region)
        response = s3.get_object(Bucket=bucket, Key=key)
        csv_data = response["Body"].read().decode("utf-8")
    except ClientError as e:
        logging.error(f"Error downloading file from S3: {e}")
        raise

    df = pd.read_csv(StringIO(csv_data), low_memory=False)
    logging.info("CSV downloaded successfully. First rows:")
    logging.info(df.head())

    return df


def list_s3_keys(
    bucket: str, prefix: str, region: str = Config.AWS_DEFAULT_REGION
) -> list:
    """List all keys in an S3 bucket with the given prefix."""
    logging.info(f"Listing keys in S3 bucket: s3://{bucket}/{prefix}")
    s3 = boto3.client("s3", region_name=region)
    keys = []
    paginator = s3.get_paginator("list_objects_v2")
    try:
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                keys.append(obj["Key"])
    except ClientError as e:
        logging.error(f"Error listing keys in S3: {e}")
        raise

    logging.info(f"Found {len(keys)} keys with prefix '{prefix}'")
    return keys


def download_s3_object(
    bucket: str, key: str, region: str = Config.AWS_DEFAULT_REGION
) -> StringIO:
    """Download an object from S3 and returns its content as a StringIO."""
    logging.info(f"Downloading object from S3: s3://{bucket}/{key}")
    try:
        s3 = boto3.client("s3", region_name=region)
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response["Body"].read().decode("utf-8")
    except ClientError as e:
        logging.error(f"Error downloading object from S3: {e}")
        raise

    return StringIO(content)
