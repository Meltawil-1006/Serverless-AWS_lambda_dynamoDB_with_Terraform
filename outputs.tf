output "function_url" {
  description = "Public HTTPS endpoint of the Lambda function"
  value       = aws_lambda_function_url.api.function_url
}

output "table_name" {
  description = "DynamoDB table name"
  value       = aws_dynamodb_table.items.name
}
