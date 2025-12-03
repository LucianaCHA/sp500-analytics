"""Silver Loader for S&P500 data."""
import logging

import pandas as pd
from base_silver_loader import BaseSilverLoader
from config import Config
from utils.aws_utils import download_s3_object, list_s3_keys


class SP500SilverLoader(BaseSilverLoader):
    """Silver Loader for S&P500 data: loads from Bronze, cleans, and saves to Silver."""

    def __init__(self):
        """Initialize S&P500 Silver Loader with Bronze and Silver S3 paths."""
        BRONZE_PATH = f"{Config.S3_BRONZE_DIR_PREFIX}/{Config.S3_BRONZE_PREFIX_SP500}"
        SILVER_PATH = f"{Config.S3_SILVER_DIR_PREFIX}/{Config.S3_SILVER_PREFIX_SP500}"
        super().__init__(bronze_prefix=BRONZE_PATH, silver_prefix=SILVER_PATH)

    def load_bronze(self) -> pd.DataFrame:
        """Load the latest Bronze S&P500 CSV file from S3."""
        keys = list_s3_keys(self.bucket, prefix=self.bronze_prefix)
        if not keys:
            raise FileNotFoundError(f"No files found in {self.bronze_prefix}")

        latest_key = sorted(keys)[-1]
        logging.info(f"Loading latest Bronze file: s3://{self.bucket}/{latest_key}")
        content = download_s3_object(self.bucket, latest_key)
        df = pd.read_csv(content)
        return df

    def clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validates the S&P500 DataFrame."""
        logging.info("Cleaning and validating S&P500 data.")
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["symbol"] = df["symbol"].str.strip().str.upper()
        df["security"] = df["security"].str.strip()

        if "symbol" not in df.columns or "security" not in df.columns:
            raise ValueError("Expected columns 'Symbol' or 'Security' not found")

        df = df.drop_duplicates(subset=["symbol"])
        return df


def main():
    """Run the SP500 Silver Loader."""
    loader = SP500SilverLoader()
    loader.run()


if __name__ == "__main__":
    main()
