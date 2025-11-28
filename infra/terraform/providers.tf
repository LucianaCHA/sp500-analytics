/*
  providers.tf
  ---------------------------------------
  Este archivo define el **proveedor de AWS**, que es el puente entre Terraform
  y la infraestructura real dentro de la nube.
  
  - Indicamos la región donde se van a crear los recursos.
  - Configuramos tags por defecto para que absolutamente todos los recursos
    creados por Terraform queden etiquetados automáticamente con:
        Project = "sp500-analytics"
        Env     = var.env
  Esto ayuda muchísimo para ordenar la cuenta de AWS y para auditoría.
*/

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project = "sp500-analytics"
      Env     = var.env
    }
  }
}


Speech corto, claro y profesional:

“Este archivo es providers.tf, y acá le digo a Terraform que vamos a trabajar con AWS como proveedor.
También especifico la región donde se van a crear todos los recursos, usando la variable var.aws_region.”

“Además, configuré default_tags.
Esto hace que absolutamente todos los recursos creados por Terraform se etiqueten automáticamente con:

Project = sp500-analytics

Env = dev/prod según la variable del entorno.”

“Esto es muy útil porque nos permite mantener ordenada la cuenta de AWS, filtrar recursos fácilmente y tener una auditoría clara.”

“En resumen, este archivo es el que conecta Terraform con AWS y establece las reglas globales para todo el proyecto.”