output "vpc_id" {
  value       = aws_vpc.main.id
  description = "The ID of the VPC"
}

output "subnet_id" {
  value       = aws_subnet.public.id
  description = "The ID of the public subnet"
}

output "security_group_id" {
  value       = aws_security_group.sec_group.id
  description = "The ID of the security group"
}

output "s3_bucket_name" {
  value       = aws_s3_bucket.backup_bucket.id
  description = "The name of the S3 bucket"
}

output "s3_bucket_arn" {
  value       = aws_s3_bucket.backup_bucket.arn
  description = "The ARN of the S3 bucket"
}

output "ec2_instance_id" {
  value       = aws_instance.web_server.id
  description = "The ID of the EC2 instance"
}

output "ec2_public_ip" {
  value       = aws_instance.web_server.public_ip
  description = "The public IP of the EC2 instance"
}

output "ec2_public_dns" {
  value       = aws_instance.web_server.public_dns
  description = "The public DNS of the EC2 instance"
}
