variable "aws_region" {
  type        = string
  description = "AWS deployment region"
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "production"
}

variable "app_name" {
  type        = string
  description = "Application identifier"
  default     = "finsight-ai"
}

variable "db_password" {
  type        = string
  description = "PostgreSQL RDS master password"
  sensitive   = true

  validation {
    condition     = length(var.db_password) >= 16
    error_message = "db_password must be supplied explicitly and contain at least 16 characters."
  }
}
