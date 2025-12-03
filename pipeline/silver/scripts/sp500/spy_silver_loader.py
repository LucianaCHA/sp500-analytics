"""Silver Loader for SPY Top 10 Holdings."""

import logging

import pandas as pd
from base_silver_loader import BaseSilverLoader
from config import Config
from utils.aws_utils import download_s3_object, list_s3_keys


class SPYSilverLoader(BaseSilverLoader):
    """
    Silver Loader for TOP 10 SPY Holdings.

    Loads the latest Bronze file, adds prices and changes, validates, and persists to Parquet.
    """

    def __init__(self):
        """Initialize SPY Silver Loader with Bronze and Silver S3 paths."""
        BRONZE_PATH = f"{Config.S3_BRONZE_DIR_PREFIX}/{Config.S3_BRONZE_PREFIX_SPY}"
        SILVER_PATH = f"{Config.S3_SILVER_DIR_PREFIX}/{Config.S3_SILVER_PREFIX_SPY}"

        super().__init__(bronze_prefix=BRONZE_PATH, silver_prefix=SILVER_PATH)

    def load_bronze(self) -> pd.DataFrame:
        """Load the latest Bronze SPY Top 10 CSV file from S3."""
        keys = list_s3_keys(self.bucket, prefix=self.bronze_prefix)
        if not keys:
            raise FileNotFoundError(f"No files found in {self.bronze_prefix}")

        latest_key = sorted(keys)[-1]
        logging.info(f"Loading latest Bronze file: s3://{self.bucket}/{latest_key}")
        content = download_s3_object(self.bucket, latest_key)
        df = pd.read_csv(content)
        return df

    def clean_and_validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validates the SPY Top 10 DataFrame."""
        logging.info("Normalizing SPY Top 10...")

        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
        df["name"] = df["name"].str.strip()
        df["holding_percent"] = pd.to_numeric(df["holding_percent"], errors="coerce")
        if "name" not in df.columns or "holding_percent" not in df.columns:
            raise ValueError("Expected columns 'Name' or 'Percent' not found")

        # # Add prices and changes
        # last_prices = []
        # prev_closes = []

        # for symbol in df.get("symbol", df["company"]):
        #     try:
        #         t = yf.Ticker(symbol)
        #         hist = t.history(period="2d")
        #         if len(hist) >= 2:
        #             prev = hist["Close"].iloc[-2]
        #             last = hist["Close"].iloc[-1]
        #         else:
        #             prev = last = None
        #     except Exception:
        #         prev = last = None

        #     last_prices.append(last)
        #     prev_closes.append(prev)

        # df["last_price"] = last_prices
        # df["prev_close"] = prev_closes
        # df["daily_change_pct"] = (
        #     (df["last_price"] - df["prev_close"]) / df["prev_close"]
        # ) * 100

        df = df.drop_duplicates(subset=["name"])
        return df


def main():
    """Run the SPY Silver Loader."""
    loader = SPYSilverLoader()
    loader.run()


if __name__ == "__main__":
    main()
