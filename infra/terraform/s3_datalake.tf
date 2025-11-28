/*
  s3_datalake.tf
  ---------------------------------------
  Este archivo define todo el **Data Lake en S3** usando el enfoque Medallion:
  - raw/
  - silver/
  - gold/

  Incluye:
  - Creación del bucket principal para los datos.
  - Habilitación de versionado (para historial y recuperación).
  - Bloqueo total de acceso público (seguridad).
  - Encriptación del bucket por defecto con AES256.
  - Creación de los prefijos/carpetas para las capas del Data Lake.

  Con esto dejamos lista la estructura donde el ETL va a escribir los datos
  procesados en cada etapa.
*/

resource "aws_s3_bucket" "data_lake" {
  bucket        = var.s3_bucket_name
  force_destroy = false

  tags = {
    Project = "sp500-analytics"
    Env     = var.env
    Owner   = var.owner_tag
  }
}

resource "aws_s3_bucket_versioning" "versioning" {
  bucket = aws_s3_bucket.data_lake.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_public_access_block" "block" {
  bucket                  = aws_s3_bucket.data_lake.id
  block_public_acls       = true
  block_public_policy     = true
  restrict_public_buckets = true
  ignore_public_acls      = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "encryption" {
  bucket = aws_s3_bucket.data_lake.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Carpetas (prefijos) para la arquitectura Medallion
resource "aws_s3_object" "raw_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "raw/"
}

resource "aws_s3_object" "clean_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "silver/"
}

resource "aws_s3_object" "curated_prefix" {
  bucket = aws_s3_bucket.data_lake.bucket
  key    = "gold/"
}

🎤 2) Qué decir en la presentación cuando muestres este archivo

Speech profesional, claro, directo:

“Este archivo se llama s3_datalake.tf y acá definimos completamente el Data Lake del proyecto.”

“Primero creamos el bucket principal (aws_s3_bucket.data_lake), que va a almacenar los datos en todas sus etapas: raw, silver y gold.”

“A ese bucket le activamos versionado, lo cual nos permite tener historial de archivos y recuperar versiones anteriores si algo falla en el ETL.”

“Después bloqueamos todo acceso público con public_access_block.
Esto es fundamental en un Data Lake porque garantiza que no haya fugas de datos.”

“También habilitamos la encriptación en servidor con AES256, que cifra todos los archivos automáticamente cuando se guardan.”

“Y finalmente creamos los prefijos raw/, silver/ y gold/.
Estos representan las tres capas del enfoque Medallion Architecture:

raw: datos crudos tal como vienen de las fuentes

silver: datos limpios y transformados

gold: datos listos para análisis o dashboards

Gracias a esta estructura, el ETL tiene un flujo claro de entrada y salida en cada etapa.”

“En resumen, este archivo deja totalmente configurado un Data Lake seguro, versionado, encriptado y organizado, listo para que el pipeline del ETL escriba cada capa de datos.”