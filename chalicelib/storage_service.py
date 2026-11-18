import boto3

class StorageService:
    def __init__(self, bucket_name):
        self.s3 = boto3.client('s3', region_name='us-east-1')
        self.bucket_name = bucket_name

    def upload(self, file_bytes, filename):
        """Upload file to S3 and return URL"""
        print(f"Uploading file to S3: {filename} ({len(file_bytes)} bytes)")
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Body=file_bytes,
                Key=filename
            )
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{filename}"
            print(f"S3 upload successful: {url}")
            return url
        except Exception as e:
            print(f"ERROR in S3 upload: {str(e)}")
            raise