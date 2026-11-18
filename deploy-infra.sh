#!/bin/bash

# Set AWS region to us-east-1
export AWS_DEFAULT_REGION=us-east-1

# Deploy CDK infrastructure
cd cdk
source .venv/bin/activate

echo "Bootstrapping CDK (if needed)..."
cdk bootstrap --region us-east-1

echo "Deploying infrastructure..."
cdk deploy --region us-east-1 --require-approval never

echo "Infrastructure deployed successfully!"
echo "Resources created:"
echo "- S3 Bucket: pkg-ship-track-images-us"
echo "- DynamoDB Table: TextDetectionTable"
echo "- IAM Role: pkg-ship-track-lambda-role"