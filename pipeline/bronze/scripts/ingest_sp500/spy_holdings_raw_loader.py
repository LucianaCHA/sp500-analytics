"""Module for loading SPY Top 10 Holdings data."""
import logging

import yfinance as yf
from base_file_loader import BaseRawFileLoader
from config import Config


class SPYTop10FileLoader(BaseRawFileLoader):
    """Fetches the raw SPY Top 10 Holdings data using yfinance and prepares it for storage in S3."""

    def __init__(self):
        """Initialize SPY Top 10 File Loader."""
        path = f"{Config.S3_BRONZE_DIR_PREFIX}/{Config.S3_BRONZE_PREFIX_SPY}"
        super().__init__(s3_prefix=path)

    def fetch_raw_file(self) -> bytes:
        """Fetch the raw SPY Top 10 Holdings data."""
        logging.info("Fetching SPY Top 10 Holdings data using yfinance.")
        spy = yf.Ticker("SPY")
        df = spy.funds_data.top_holdings.head(10)
        return df.to_csv(index=False).encode("utf-8")

    def get_file_name(self) -> str:
        """Get the file name for the raw SPY Top 10 Holdings data."""
        return f"{Config.S3_BRONZE_PREFIX_SPY}.csv"


def main():
    """Run the SPY Top 10 File Loader."""
    loader = SPYTop10FileLoader()
    loader.run()


if __name__ == "__main__":
    main()
