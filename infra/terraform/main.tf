terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# S3 principal del proyecto
resource "aws_s3_bucket" "data_lake" {
  bucket = var.s3_bucket_name

  tags = {
    Project = "sp500-analytics"
    Env     = var.env
    Owner   = var.owner_tag
  }
}

# Versionado del bucket (buena práctica)
resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

# "Carpetas" lógicas dentro del bucket (raw/clean/curated)
resource "aws_s3_object" "raw_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "raw/"
}

resource "aws_s3_object" "clean_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "clean/"
}

resource "aws_s3_object" "curated_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "curated/"
}