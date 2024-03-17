provider "aws" {
  region = "eu-central-1"
}

# Define the IAM policy for SageMaker and S3 access
resource "aws_iam_policy" "sagemaker_s3_full_access" {
  name        = "SageMaker_S3FullAccessPoliciy"
  description = "Policy for full access to SageMaker and S3"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "sagemaker:*",
          "s3:*"
        ],
        Resource = "*"
      }
    ]
  })
}

# Define the IAM role
resource "aws_iam_role" "sagemaker_role" {
  name = "AnimeRecommendation_SageMakerRole"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Effect    = "Allow",
      Principal = {
        Service = "sagemaker.amazonaws.com"
      },
      Action    = "sts:AssumeRole"
    }]
  })
}

# Attach the IAM policy to the IAM role
resource "aws_iam_role_policy_attachment" "sagemaker_s3_policy_attachment" {
  role       = aws_iam_role.sagemaker_role.name
  policy_arn = aws_iam_policy.sagemaker_s3_full_access.arn
}

resource "aws_sagemaker_notebook_instance" "notebookinstance" {
    name = "anime-recommendation-system-notebook"
    role_arn = aws_iam_role.sagemaker_role.arn
    instance_type = "ml.t3.medium"
}