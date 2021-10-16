module "gateway-api" {
  source              = "../../gateway-api/config"
  namespace           = var.env_id
  backend_ingress_url = var.backend_ingress_url
  tld_name            = var.tld_name
  certificate_arn     = var.certificate_arn
}

output "gatewayapi_post_new_url" {
  value = "curl -XPOST '${module.gateway-api.base_url}/new-post?name=Alice&message=Watson+come+here+I+need+you'"
}
