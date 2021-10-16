locals {
  api_hostname = "${var.namespace}-api.${var.tld_name}"
}

variable "namespace" {
  type        = string
  description = "The namespace for this module."
}

variable "stage_name" {
  type        = string
  description = "The name of the stage, prod, staging, or v1, v2, etc."
  default     = "v1"
}

variable "certificate_arn" {
  type        = string
  description = "ARN for the ACM certificate in us-east-1."
}

variable "tld_name" {
  type        = string
  description = "The dns name for the tld"
}

variable "backend_ingress_url" {
  type        = string
  description = "Nodejs api backend endpoint."
}
