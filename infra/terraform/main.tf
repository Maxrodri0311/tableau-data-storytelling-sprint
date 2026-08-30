terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "environment" {
  type    = string
  default = "production"
}

# 1. S3 Lakehouse Bucket for Talent Acquisition Telemetry
resource "aws_s3_bucket" "talent_lakehouse" {
  bucket        = "apply-on-job-talent-lakehouse-${var.environment}"
  force_destroy = false

  tags = {
    Environment = var.environment
    Domain      = "TalentAnalytics"
    Project     = "GP-026-Apply-on-Job"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "talent_crypto" {
  bucket = aws_s3_bucket.talent_lakehouse.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# 2. AWS Glue Catalog for Recruitment Dimensional Schema
resource "aws_glue_catalog_database" "recruitment_catalog" {
  name        = "apply_on_job_recruitment_analytics"
  description = "AWS Glue Catalog for Apply on Job Star Schema & Candidate Funnel"
}

# 3. AWS Athena Analytics Workgroup
resource "aws_athena_workgroup" "recruitment_workgroup" {
  name        = "apply-on-job-analytics-wg"
  description = "Athena Workgroup for Sub-second OLAP & Tableau Connector Queries"

  configuration {
    enforce_workgroup_configuration    = true
    publish_cloudwatch_metrics_enabled = true

    result_configuration {
      output_location = "s3://${aws_s3_bucket.talent_lakehouse.bucket}/athena_results/"
      encryption_configuration {
        encryption_option = "SSE_S3"
      }
    }
  }
}
