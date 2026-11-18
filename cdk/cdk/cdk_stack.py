from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    RemovalPolicy,
    CfnOutput
)
from constructs import Construct

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 Bucket for images
        self.image_bucket = s3.Bucket(
            self, "ImageBucket",
            bucket_name=f"pkg-ship-track-images-{self.account}-us",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True
        )

        # DynamoDB Table for text detection records
        self.text_table = dynamodb.Table(
            self, "TextDetectionTable",
            table_name="TextDetectionTable",
            partition_key=dynamodb.Attribute(
                name="user_id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="record_id", 
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY
        )

        # IAM Role for Chalice Lambda
        self.lambda_role = iam.Role(
            self, "ChaliceLambdaRole",
            role_name="pkg-ship-track-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ]
        )

        # Grant permissions
        self.image_bucket.grant_read_write(self.lambda_role)
        self.text_table.grant_read_write_data(self.lambda_role)
        
        # Textract and Comprehend permissions
        self.lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "textract:DetectDocumentText",
                    "comprehend:DetectEntities"
                ],
                resources=["*"]
            )
        )

        # Output the role ARN for Chalice configuration
        CfnOutput(
            self, "LambdaRoleArn",
            value=self.lambda_role.role_arn,
            description="IAM Role ARN for Chalice Lambda functions"
        )
