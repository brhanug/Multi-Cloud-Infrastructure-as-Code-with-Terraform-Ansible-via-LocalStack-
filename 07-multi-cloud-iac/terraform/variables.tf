variable "aws_region" {
  type        = string
  description = "The AWS region to provision resources in"
  default     = "us-east-1"
}

variable "localstack_endpoint" {
  type        = string
  description = "The endpoint URL for LocalStack"
  default     = "http://localhost:4566"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "dev"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t2.micro"
}

variable "ami_id" {
  type        = string
  description = "The AMI ID to use for the EC2 instance"
  # In LocalStack, any AMI ID works, but standard custom or mock IDs are used
  default     = "ami-12345678"
}
