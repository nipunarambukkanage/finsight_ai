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
  default     = "FinSightSecureDBPass2025!"
}
