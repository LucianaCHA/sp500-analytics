/*
Este archivo se llama backend.tf.
Acá le digo a Terraform dónde guardar el estado de la infraestructura.
En vez de tener el terraform.tfstate local en cada máquina, 
lo guardamos en un bucket de S3, en esta ruta prod/terraform.tfstate.
Eso hace que el estado sea compartido y consistente para 
todo el equipo y que podamos mantener la infraestructura sincronizada desde cualquier lugar.
*/

terraform {
  backend "s3" {
    bucket = "sp500-terraform-state-henry"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}
