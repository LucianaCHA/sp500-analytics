/*
  compute.tf
  ------------------------------------
  Este archivo define la **parte de cómputo** de la infraestructura:
  - Crea la instancia EC2 donde corre nuestro ETL (`aws_instance.etl_server`).
  - Le asocia el security group, el rol IAM y el key pair para acceso por SSH.
  - Usa `user_data` para instalar Docker y levantar automáticamente el contenedor del ETL
    desde Docker Hub, sin intervención manual.
  - Crea una Elastic IP (`aws_eip.etl_ip`) para que la instancia tenga siempre
    la misma IP pública, incluso si se reinicia o se recrea.
*/

resource "aws_instance" "etl_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_1a.id
  vpc_security_group_ids = [aws_security_group.etl_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.etl_instance_profile.name

  # 👉 Key pair para poder entrar por SSH
  key_name = var.key_name

  tags = {
    Name    = "sp500-etl-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }

  # Script que se ejecuta automáticamente al crear la instancia
  user_data = <<-EOF
    #!/bin/bash
    set -e

    # Log básico para debug en /var/log/cloud-init-output.log
    echo "=== Iniciando user_data de sp500-etl ==="

    # Actualizar e instalar Docker (funciona para Ubuntu o Amazon Linux)
    if command -v apt-get >/dev/null 2>&1; then
      echo "Detectado sistema basado en Debian/Ubuntu"
      apt-get update -y
      apt-get install -y docker.io
    else
      echo "Detectado sistema basado en RHEL/Amazon Linux"
      yum update -y
      amazon-linux-extras install docker -y || yum install -y docker
    fi

    systemctl enable docker
    systemctl start docker

    echo "Docker instalado, iniciando pull de la imagen"

    # PULL de la última imagen desde Docker Hub
    sudo docker pull ${var.dockerhub_username}/sp500-etl:latest

    # Si existe un contenedor anterior con ese nombre, lo limpiamos
    if sudo docker ps -a --format '{{.Names}}' | grep -q '^sp500-etl$'; then
      sudo docker stop sp500-etl || true
      sudo docker rm sp500-etl || true
    fi

    # Levantamos el contenedor (ajustá puertos/variables si hace falta)
    sudo docker run -d \
      --name sp500-etl \
      --restart unless-stopped \
      -p 8080:8080 \
      -e AIRFLOW__CORE__LOAD_EXAMPLES=False \
      ${var.dockerhub_username}/sp500-etl:latest

    echo "=== user_data de sp500-etl finalizado ==="
  EOF
}

resource "aws_eip" "etl_ip" {
  instance = aws_instance.etl_server.id
  domain   = "vpc"

  tags = {
    Name    = "sp500-etl-ip-${var.env}"
    Project = "sp500-analytics"
    Env     = var.env
  }
}

/*

2) Qué decir cuando muestres este archivo (guion hablado)

Te dejo un speech cortito que podés usar casi textual:

“Este archivo se llama compute.tf y define toda la parte de cómputo del proyecto.
Acá creamos la instancia EC2 donde corre nuestro ETL, que es este recurso aws_instance.etl_server.

A la instancia le asociamos:

el tipo de instancia y la AMI que usamos (var.instance_type, var.ami_id),

la subred pública donde va a vivir,

el security group que le abre sólo los puertos necesarios,

y el rol IAM para que pueda hablar con S3 y el resto de servicios.
También le pasamos un key pair para poder entrar por SSH si hace falta debug.”

“Lo más interesante es este bloque de user_data.
Es un script que se ejecuta automáticamente cuando la instancia se crea.
Lo que hace es:

Detectar el sistema operativo (Ubuntu o Amazon Linux).

Instalar y habilitar Docker.

Hacer docker pull de la imagen del ETL que publicamos en Docker Hub.

Si había un contenedor viejo sp500-etl, lo detiene y lo borra.

Levanta el contenedor nuevo con docker run y lo deja configurado para reiniciarse solo si la máquina se reinicia.

Con esto logramos que, cada vez que Terraform crea o recrea la EC2, la máquina se autoconfigure y deje corriendo la última versión del ETL sin que nadie tenga que entrar a configurar nada a mano.”

“Abajo tenemos otro recurso, aws_eip.etl_ip, que crea una Elastic IP y se la asocia a esta instancia.
Esto nos garantiza que la instancia tenga siempre la misma IP pública, aunque la paremos, la prendamos o la recreemos desde Terraform.
Eso es clave para conectarnos desde afuera y para los pipelines de despliegue.”
*/