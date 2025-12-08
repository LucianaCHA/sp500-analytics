########################################
# ZIP de la Lambda
########################################

data "archive_file" "start_airflow_zip" {
  type = "zip"
  # 👇 El .py está en ../lambda relativo a este módulo terraform
  source_file = "${path.module}/../lambda/start_airflow_lambda.py"
  output_path = "${path.module}/../lambda/start_airflow_lambda.zip"
}

########################################
# IAM Role + Policy para la Lambda
########################################

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

########################################
# Lambda que enciende la EC2 y redirige a Airflow
########################################

resource "aws_lambda_function" "start_airflow" {
  function_name = "start-airflow-on-demand-${var.env}"
  role          = aws_iam_role.start_airflow_lambda_role.arn
  handler       = "start_airflow_lambda.lambda_handler"
  runtime       = "python3.12"

  filename         = data.archive_file.start_airflow_zip.output_path
  source_code_hash = data.archive_file.start_airflow_zip.output_base64sha256

  environment {
    variables = {
      INSTANCE_ID = aws_instance.etl_server.id
      AIRFLOW_URL = "http://${aws_eip.etl_ip.public_ip}:8080"
    }
  }

  timeout = 15
}

########################################
# API Gateway HTTP API
########################################

resource "aws_apigatewayv2_api" "airflow_on_demand_api" {
  name          = "airflow-on-demand-api-${var.env}"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "airflow_on_demand_integration" {
  api_id                 = aws_apigatewayv2_api.airflow_on_demand_api.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.start_airflow.invoke_arn
  integration_method     = "POST"
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "airflow_on_demand_route" {
  api_id    = aws_apigatewayv2_api.airflow_on_demand_api.id
  route_key = "GET /"

  target = "integrations/${aws_apigatewayv2_integration.airflow_on_demand_integration.id}"
}

resource "aws_apigatewayv2_stage" "airflow_on_demand_stage" {
  api_id      = aws_apigatewayv2_api.airflow_on_demand_api.id
  name        = "$default"
  auto_deploy = true
}

########################################
# Permiso para que API Gateway invoque la Lambda
########################################

resource "aws_lambda_permission" "allow_apigw_to_invoke" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start_airflow.function_name
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_apigatewayv2_api.airflow_on_demand_api.execution_arn}/*/*"
}

########################################
# Output con la URL pública
########################################

output "airflow_on_demand_url" {
  description = "URL pública para acceder a Airflow de forma on-demand"
  value       = aws_apigatewayv2_api.airflow_on_demand_api.api_endpoint
}