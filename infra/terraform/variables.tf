variable "aws_region" {
  description = "Región AWS donde se despliega la infraestructura del Data Lake para el proyecto SP500 Analytics. Se usa para asegurar consistencia entre servicios (S3, RDS, IAM, etc.)."
  type        = string
  default     = "us-east-1"
}

variable "env" {
  description = "Entorno lógico del despliegue (dev, test o prod). Permite diferenciar infraestructura entre ambientes y seguir buenas prácticas de DevOps."
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Nombre del bucket S3 que funcionará como Data Lake del proyecto. Almacena las zonas raw, clean y curated utilizadas en el pipeline del S&P500."
  type        = string
}

variable "owner_tag" {
  description = "Etiqueta que identifica al responsable del despliegue o al equipo del proyecto. Útil para auditoría, organización y gobernanza en AWS."
  type        = string
  default     = "sp500-henry-team"
}
