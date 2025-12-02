resource "aws_db_subnet_group" "rds" {
  name       = "${var.app_name}-db-subnet-group"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_db_instance" "postgres" {
  identifier          = "${var.app_name}-db"
  allocated_storage   = 20
  max_allocated_storage = 100
  engine              = "postgres"
  engine_version      = "16.3"
  instance_class      = "db.t4g.medium"
  db_name             = "finsight_ai"
  username            = "postgres"
  password            = var.db_password
  db_subnet_group_name = aws_db_subnet_group.rds.name
  skip_final_snapshot = true

  tags = {
    Name = "${var.app_name}-postgres-pgvector"
  }
}
