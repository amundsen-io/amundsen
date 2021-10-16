data "aws_route53_zone" "tld" {
  name         = "${var.tld_name}."
  private_zone = false
}

resource "aws_route53_record" "this" {
  name    = local.api_hostname
  type    = "A"
  zone_id = data.aws_route53_zone.tld.id

  alias {
    evaluate_target_health = true
    name                   = aws_api_gateway_domain_name.this.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.this.cloudfront_zone_id
  }
}

output "custom_domain_name" {
  value = aws_route53_record.this.fqdn
}
