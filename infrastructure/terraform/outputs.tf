output "vpc_id" {
  value       = aws_vpc.main.id
  description = "VPC Identifier"
}

output "rds_endpoint" {
  value       = aws_db_instance.postgres.endpoint
  description = "PostgreSQL RDS connection endpoint"
}

output "cloudfront_domain" {
  value       = aws_cloudfront_distribution.cdn.domain_name
  description = "CloudFront CDN domain URL"
}

output "s3_filings_bucket" {
  value       = aws_s3_bucket.documents.bucket
  description = "S3 bucket for financial report storage"
}
