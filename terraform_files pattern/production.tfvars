# Production environment variables
aws_region = "us-west-2"
environment = "prod"
instance_count = 5
instance_type = "t3.medium"

# Production-specific settings
enable_monitoring = true
backup_retention_period = 30

# Production tags
common_tags = {
  Environment = "production"
  Project     = "terraform-to-json-demo"
  ManagedBy   = "terraform"
  Owner       = "devops-team"
  CostCenter  = "engineering"
}
