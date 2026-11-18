#!/bin/bash

# Destroy CDK infrastructure
cd cdk
source .venv/bin/activate

echo "Destroying infrastructure..."
cdk destroy --force

echo "Infrastructure destroyed successfully!"
echo "Resources deleted:"
echo "- S3 Bucket: pkg-ship-track-images-186814813507-ca"
echo "- DynamoDB Table: TextDetectionTable"
echo "- IAM Role: ChaliceLambdaRole"