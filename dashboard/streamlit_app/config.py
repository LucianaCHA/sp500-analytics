"""Configuration module for pipeline settings."""

import os

NOT_SET = "not_set"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", NOT_SET)
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", NOT_SET)
AWS_DEFAULT_REGION = os.getenv("AWS_DEFAULT_REGION", NOT_SET)

# Bucket (lo estás seteando como S3_BUCKET en tu deploy)
AWS_S3_BUCKET_NAME = os.getenv("S3_BUCKET", NOT_SET)

# Gold path configurable
AWS_S3_GOLD_DIR_PREFIX = os.getenv("AWS_S3_GOLD_DIR_PREFIX", "gold")
AWS_S3_GOLD_PREFIX_SP500_DAILY_PRICES = os.getenv(
    "AWS_S3_GOLD_PREFIX_SP500_DAILY_PRICES", "sp500_daily_prices"
)
AWS_S3_GOLD_FILENAME = os.getenv("AWS_S3_GOLD_FILENAME", "sp500_gold.parquet")


class Config:
    """Configuration class for streamlit settings."""

    AWS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
    AWS_DEFAULT_REGION = AWS_DEFAULT_REGION

    AWS_S3_BUCKET_NAME = AWS_S3_BUCKET_NAME

    # base prefix: gold/sp500_daily_prices
    AWS_S3_GOLD_BASE_PREFIX = (
        f"{AWS_S3_GOLD_DIR_PREFIX}/{AWS_S3_GOLD_PREFIX_SP500_DAILY_PRICES}"
    ).rstrip("/")

    AWS_S3_GOLD_FILENAME = AWS_S3_GOLD_FILENAME