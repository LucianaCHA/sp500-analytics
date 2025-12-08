resource "aws_iam_role" "start_airflow_lambda_role" {
  name = "start-airflow-lambda-role-${var.env}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "start_airflow_lambda_policy" {
  name = "start-airflow-lambda-policy-${var.env}"
  role = aws_iam_role.start_airflow_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      # Permisos para manejar la instancia EC2
      {
        Effect = "Allow"
        Action = [
          "ec2:DescribeInstances",
          "ec2:StartInstances"
        ]
        Resource = "*"
      },
      # Logs en CloudWatch
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "*"
      }
    ]
  })
}
