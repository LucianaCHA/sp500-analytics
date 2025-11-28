/*
  network.tf
  ---------------------------------------
  Este archivo define toda la **red base** del proyecto en AWS:
  - Una VPC propia para el proyecto (aislamiento de red).
  - Una subred pública donde vive la instancia del ETL.
  - Un Internet Gateway para sacar el tráfico a internet.
  - Una Route Table que manda todo el tráfico externo (0.0.0.0/0) por ese gateway.
  - La asociación entre la subred y esa tabla de ruteo.
  
  En resumen: acá dejamos lista la red para que la EC2 del ETL pueda tener
  IP pública, salir a internet y ser accesible desde afuera de forma controlada.
*/

resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name    = "sp500-vpc-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_subnet" "public_1a" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = var.public_subnet_1a_cidr
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name    = "sp500-public-1a-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name    = "sp500-igw-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  tags = {
    Name    = "sp500-public-rt-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_1a.id
  route_table_id = aws_route_table.public_rt.id
}

/*

2) Guion para explicarlo en la presentación

Cuando lo muestres, podés decir algo así:

“Este archivo es network.tf y acá definimos toda la red del proyecto dentro de AWS.”

“Primero creamos una VPC propia (aws_vpc.main).
Esto nos da una red aislada, con su propio rango de IPs, soporte de DNS y hostnames.
La idea es que todo lo del proyecto SP500 viva dentro de esta VPC, separado de otras cosas de la cuenta.”

“Después definimos una subred pública (aws_subnet.public_1a).
Está en una zona de disponibilidad específica (${var.aws_region}a) y tiene map_public_ip_on_launch = true,
eso significa que las instancias que lancemos ahí van a tener IP pública, que es lo que usamos para exponer la EC2 del ETL.”

“Acá creamos el Internet Gateway (aws_internet_gateway.igw), que es básicamente la puerta de salida a internet para la VPC.”

“Con aws_route_table.public_rt definimos una route table pública:
tiene una ruta 0.0.0.0/0 que manda todo el tráfico hacia afuera por el Internet Gateway.
O sea: cualquier tráfico que salga de la VPC hacia internet, pasa por ese gateway.”

“Y finalmente, con aws_route_table_association.public_assoc asociamos esa tabla de ruteo a la subred pública.
Eso hace que las instancias en esa subnet tengan salida a internet y puedan, por ejemplo,
hacer docker pull de la imagen del ETL en Docker Hub, o ser accesibles desde nuestra máquina para debug.”

“En resumen: con este archivo dejamos lista la base de red para el proyecto:
VPC aislada, subred pública para el ETL y conexión controlada a internet.”

*/