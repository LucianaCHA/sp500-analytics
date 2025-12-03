import logging
from datetime import datetime

import boto3
import pandas as pd
from config import Config


class BaseSilverLoader:
    """Base class for loading Silver data from S3."""

    def __init__(self, bronze_prefix: str, silver_prefix: str):
        """Initialize Base Silver Loader with Bronze and Silver S3 prefixes."""
        self.bucket = Config.S3_BUCKET
        self.region = Config.AWS_DEFAULT_REGION
        self.s3 = boto3.client("s3", region_name=self.region)
        self.bronze_prefix = bronze_prefix
        self.silver_prefix = silver_prefix

    def load_bronze(self) -> pd.DataFrame:
        """Implement in subclass: normalization, types, validations."""
        raise NotImplementedError

    def clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Implement in subclass: normalization, types, validations."""
        raise NotImplementedError

    # def save_silver(self, df: pd.DataFrame):
    #     now = datetime.utcnow()
    #     date_path = now.strftime("%Y/%m/%d")
    #     time_stamp = now.strftime("%H%M%S")
    #     file_name = f"{self.silver_prefix.split('/')[-1]}_clean_{time_stamp}.parquet"
    #     s3_key = f"{self.silver_prefix}/{date_path}/{file_name}"

    #     logging.info(f"Saving Silver Parquet: s3://{self.bucket}/{s3_key}")
    #     df.to_parquet(f"s3://{self.bucket}/{s3_key}", index=False)

    def file_exists(self, s3_key: str) -> bool:
        """Check if a file exists in S3 at the given key."""
        try:
            self.s3.head_object(Bucket=self.bucket, Key=s3_key)
            return True
        except self.s3.exceptions.ClientError:
            return False

    def save_silver(self, df: pd.DataFrame, force: bool = False):
        """
        Save Silver to S3 as Parquet with date/time, without overwriting existing files

        unless force=True is specified.
        """
        now = datetime.utcnow()
        date_path = now.strftime("%Y/%m/%d")
        time_stamp = now.strftime("%H%M%S")
        file_name = f"{self.silver_prefix.split('/')[-1]}_clean_{time_stamp}.parquet"
        s3_key = f"{self.silver_prefix}/{date_path}/{file_name}"

        if not force and self.file_exists(s3_key):
            logging.info(
                f"File already exists, skipping save: s3://{self.bucket}/{s3_key}"
            )
            return

        logging.info(f"Saving Silver Parquet: s3://{self.bucket}/{s3_key}")
        df.to_parquet(f"s3://{self.bucket}/{s3_key}", index=False)

    def run(self):
        """Execute the Silver loading process: load Bronze, clean/validate, save Silver."""
        logging.info(f"===== SILVER LOAD: {self.__class__.__name__} =====")
        df = self.load_bronze()
        df_clean = self.clean_and_validate(df)
        self.save_silver(df_clean)
        logging.info("===== END SILVER LOAD =====\n")
