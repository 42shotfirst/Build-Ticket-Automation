# S3 Bucket configuration
resource "aws_s3_bucket" "data" {
  bucket = "${local.project_name}-${local.environment}-data-${random_string.bucket_suffix.result}"

  tags = merge(local.common_tags, {
    Name = "${local.project_name}-data-bucket"
    Type = "data"
  })
}

resource "aws_s3_bucket_versioning" "data" {
  bucket = aws_s3_bucket.data.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "data" {
  bucket = aws_s3_bucket.data.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "random_string" "bucket_suffix" {
  length  = 8
  special = false
  upper   = false
}

# IAM role for S3 access
resource "aws_iam_role" "s3_access" {
  name = "${local.project_name}-s3-access-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy" "s3_access" {
  name = "${local.project_name}-s3-access-policy"
  role = aws_iam_role.s3_access.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.data.arn}/*"
      }
    ]
  })
}

resource "aws_iam_instance_profile" "s3_access" {
  name = "${local.project_name}-s3-access-profile"
  role = aws_iam_role.s3_access.name

  tags = local.common_tags
}
