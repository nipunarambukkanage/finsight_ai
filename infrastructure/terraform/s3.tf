resource "aws_s3_bucket" "documents" {
  bucket = "${var.app_name}-documents-${var.environment}"

  tags = {
    Name = "FinSight SEC Filings Storage"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "docs_enc" {
  bucket = aws_s3_bucket.documents.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket" "frontend" {
  bucket = "${var.app_name}-frontend-${var.environment}"

  tags = {
    Name = "FinSight Frontend Web Assets"
  }
}
