# Mostly stolen from https://learn.hashicorp.com/tutorials/terraform/lambda-api-gateway

resource "aws_api_gateway_rest_api" "this" {
  name        = "${var.namespace}-api"
  description = "Gateway API external endpoints"

  endpoint_configuration {
    types = [
      "EDGE",
    ]
  }
}

# This creates the "new" matcher
resource "aws_api_gateway_resource" "new" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  parent_id   = aws_api_gateway_rest_api.this.root_resource_id
  path_part   = "new-post"
}

resource "aws_api_gateway_method" "post_new" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_resource.new.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "post_new" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_method.post_new.resource_id
  http_method = aws_api_gateway_method.post_new.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.post_new.invoke_arn
}

# This creates the "root" or empty match
resource "aws_api_gateway_method" "any_root" {
  rest_api_id   = aws_api_gateway_rest_api.this.id
  resource_id   = aws_api_gateway_rest_api.this.root_resource_id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "any_root" {
  rest_api_id = aws_api_gateway_rest_api.this.id
  resource_id = aws_api_gateway_method.any_root.resource_id
  http_method = aws_api_gateway_method.any_root.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = data.aws_lambda_function.post_new.invoke_arn
}

resource "aws_api_gateway_deployment" "this" {
  # This depends on is weak because you sould infer it from triggers, which is identical
  depends_on = [
    aws_api_gateway_integration.post_new,
    aws_api_gateway_integration.any_root,
  ]

  rest_api_id = aws_api_gateway_rest_api.this.id
  stage_name  = var.stage_name

  triggers = {
    post_new_arn = data.aws_lambda_function.post_new.invoke_arn

    # See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment#redeployment-triggers
    redeployment = sha1(join(",", list(
      jsonencode(aws_api_gateway_integration.any_root),
      jsonencode(aws_api_gateway_integration.post_new),
    )))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_domain_name" "this" {
  certificate_arn = var.certificate_arn
  domain_name     = local.api_hostname
}

resource "aws_api_gateway_base_path_mapping" "this" {
  api_id      = aws_api_gateway_rest_api.this.id
  stage_name  = aws_api_gateway_deployment.this.stage_name
  domain_name = aws_api_gateway_domain_name.this.domain_name
}

output "base_url" {
  value = aws_api_gateway_deployment.this.invoke_url
}

output "cloudfront_domain_name" {
  value = aws_api_gateway_domain_name.this.cloudfront_domain_name
}
