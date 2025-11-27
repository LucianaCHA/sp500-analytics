resource "aws_instance" "etl_server" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.public_1a.id
  vpc_security_group_ids = [aws_security_group.etl_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.etl_instance_profile.name

  # 👉 NUEVO: asociar el key pair de AWS para poder entrar por SSH
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

    # Por si el usuario no está en el grupo docker, usamos sudo siempre
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
