import logging

import pandas as pd
from base_file_loader import BaseRawFileLoader
from config import Config


class SP500FileLoader(BaseRawFileLoader):
    """Fetch the raw S&P500 CSV file from a public URL and prepares it for storage in S3."""

    def __init__(self):
        """Initialize S&P500 File Loader."""
        path = f"{Config.S3_BRONZE_DIR_PREFIX}/{Config.S3_BRONZE_PREFIX_SP500}"
        super().__init__(s3_prefix=path)

    def fetch_raw_file(self) -> bytes:
        """Fetch the raw S&P500 CSV file from the public URL."""
        logging.info("Fetching S&P500 raw file from public URL.")
        df = pd.read_csv(Config.SP500_URL)
        df.columns = df.columns.str.strip().str.replace("\ufeff", "")
        return df.to_csv(index=False).encode("utf-8")

    def get_file_name(self) -> str:
        """Get the file name for the raw S&P500 data."""
        return f"{Config.S3_BRONZE_PREFIX_SP500}.csv"


def main():
    """Run the SP500 File Loader."""
    loader = SP500FileLoader()
    loader.run()


if __name__ == "__main__":
    main()
