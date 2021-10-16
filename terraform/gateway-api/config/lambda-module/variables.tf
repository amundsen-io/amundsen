variable "function_name" {
  type        = string
  description = "The name of the lambda function"
}

variable "filename" {
  type        = string
  description = "The filename where the source code is."
  default     = "index.js"
}

variable "memory_size" {
  type        = number
  description = "The amount of KBi to use."
  default     = 128
}

variable "timeout" {
  type        = number
  description = "The number of seconds before lambda will timeout."
  default     = 5
}

variable "lambda_iam_role_arn" {
  type        = string
  description = "The ARN for the lambda execution role."
}

variable "handler" {
  type        = string
  description = "The name of the function handler entrypoint."
  default     = "index.datadogHandler"
}

variable "runtime" {
  type        = string
  description = "The name of the runtime interpreter."
  default     = "nodejs12.x"
}

variable "backend_ingress_url" {
  type        = string
  description = "Nodejs api backend endpoint."
}

variable "namespace" {
  type = string
  description = "The namespace for multiple environment support."
}
