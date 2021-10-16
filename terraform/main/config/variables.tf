variable "env_id" {
  type        = string
  description = "The name of the environment namespace"
}

variable "certificate_arn" {
  type        = string
  description = "ARN for the ACM certificate in us-east-1."
}

variable "tld_name" {
  type        = string
  description = "The DNS name where the application is deployed."
}

variable "backend_ingress_url" {
  type        = string
  description = "Nodejs api backend endpoint."
}
