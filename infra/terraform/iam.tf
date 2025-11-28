/*
  iam.tf
  ---------------------------------------
  Este archivo define toda la capa de IAM para la instancia del ETL.
  
  Contiene:
  - Un **IAM Role** que puede ser asumido por EC2.
  - Una **política IAM** con permisos mínimos para acceder al Data Lake en S3
    (ListBucket, GetObject, PutObject y DeleteObject dentro del bucket).
  - La asociación entre el role y la política.
  - Un **Instance Profile**, que es lo que realmente se adjunta a la EC2.
  
  Sin estos recursos, la instancia no podría leer ni escribir datos en S3.
*/

resource "aws_iam_role" "etl_role" {
  name = "sp500-etl-role-v3-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })

  tags = {
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_iam_policy" "etl_s3_policy" {
  name        = "sp500-etl-s3-policy-${var.env}"
  description = "Permite acceso al Data Lake S3 para la instancia ETL"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["s3:ListBucket"]
        Resource = [aws_s3_bucket.data_lake.arn]
      },
      {
        Effect   = "Allow"
        Action   = ["s3:GetObject", "s3:PutObject", "s3:DeleteObject"]
        Resource = ["${aws_s3_bucket.data_lake.arn}/*"]
      }
    ]
  })

  tags = {
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_iam_role_policy_attachment" "etl_role_attach" {
  role       = aws_iam_role.etl_role.name
  policy_arn = aws_iam_policy.etl_s3_policy.arn
}

resource "aws_iam_instance_profile" "etl_instance_profile" {
  name = "sp500-etl-instance-profile-${var.env}-v2"
  role = aws_iam_role.etl_role.name
}

/*

“Este archivo se llama iam.tf y define todos los permisos que necesita la instancia del ETL para trabajar con el Data Lake.

Primero creamos un IAM Role, que es este recurso aws_iam_role.etl_role.
Este role está configurado con una assume_role_policy que permite que EC2 lo asuma.
Es decir: la instancia va a ‘tomar’ este role automáticamente cuando arranque.

Después definimos esta política: aws_iam_policy.etl_s3_policy.
Esta política da acceso mínimo y controlado al Data Lake en S3:

Puede listar el bucket,

y puede obtener, subir o borrar objetos solo dentro del bucket del Data Lake.

Esto sigue el principio de mínimo privilegio: la instancia del ETL no puede tocar nada más que lo que realmente necesita.”

“Acá abajo está el aws_iam_role_policy_attachment, que simplemente asocia esa política al role.”

“Y finalmente, creamos un aws_iam_instance_profile.
El Instance Profile es lo que realmente adjuntamos a la EC2.
Gracias a eso, cuando la instancia se levanta, ya tiene permisos para conectarse al Data Lake sin que tengamos que gestionar claves o secretos.”

“Con esta configuración logramos que la EC2 pueda leer y escribir datos en S3 de forma segura, auditada y sin credenciales expuestas.”

*/