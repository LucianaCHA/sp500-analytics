"""Module defining a base class for loading raw files into S3."""
import logging
from datetime import datetime

import boto3
from config import Config


class BaseRawFileLoader:
    """
    Generic base class for loading raw files into S3.

    Each concrete loader must implement the `fetch_raw_file` and `get_file_name` methods
    """

    def __init__(self, s3_prefix: str):
        """Initialize the base raw file loader."""
        self.bucket = Config.S3_BUCKET
        self.region = Config.AWS_DEFAULT_REGION
        self.s3_prefix = s3_prefix
        self.s3 = boto3.client("s3", region_name=self.region)

    def fetch_raw_file(self) -> bytes:
        """Fetch the raw file content and return it as bytes."""
        raise NotImplementedError

    def get_file_name(self) -> str:
        """Return the desired file name for the raw file."""
        raise NotImplementedError

    def upload_to_s3(self, content: bytes, key: str):
        """Upload the given content to S3 at the specified key."""
        logging.info(
            f"Uploading file RAW → s3://{self.bucket}/{key}, size: {len(content)} bytes"
        )
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=content)

    def generate_s3_key(
        self,
        date_format: str = "%Y/%m/%d",
        include_timestamp: bool = True,
        timestamp_format: str = "%H%M%S",
    ) -> str:
        """
        Generate the S3 key including date-based directory and optional timestamped file name.

        Args:
            date_format: str, format for the directory path (default: "%Y/%m/%d")
            include_timestamp: bool, whether to append a timestamp to the file name (default: True)
            timestamp_format: str, format of the timestamp (default: "%H%M%S")

        Returns:
            str: Full S3 key
        """
        now = datetime.utcnow()
        date_path = now.strftime(date_format)
        file_name = self.get_file_name().replace(".csv", "")
        if include_timestamp:
            time_stamp = now.strftime(timestamp_format)
            file_name = f"{file_name}_{time_stamp}.csv"
        else:
            file_name = f"{file_name}.csv"
        return f"{self.s3_prefix}/{date_path}/{file_name}"

    def run(self):
        """Execute the raw file loading process."""
        logging.info(f"\n===== RAW FILE LOAD: {self.__class__.__name__} =====")
        content = self.fetch_raw_file()
        s3_key = self.generate_s3_key()

        # # Timestamp UTC
        # now = datetime.utcnow()
        # date_path = now.strftime("%Y/%m/%d")
        # time_stamp = now.strftime("%H%M%S")
        # file_name = f"{self.get_file_name().replace('.csv', '')}_{time_stamp}.csv"

        # s3_key = f"{self.s3_prefix}/{date_path}/{file_name}"
        self.upload_to_s3(content, s3_key)

        logging.info(f"Saved in: s3://{self.bucket}/{s3_key}")
        logging.info("===== END RAW FILE LOAD =====\n")
