import boto3

class TextDetectionService:
    def __init__(self, storage_service):
        self.textract = boto3.client('textract', region_name='us-east-1')
        self.storage = storage_service

    def extract_text(self, filename, min_confidence=75.0):
        """Extract text from image using AWS Textract"""
        print(f"Starting Textract extraction for: {filename} (min confidence: {min_confidence})")
        try:
            response = self.textract.detect_document_text(
                Document={
                    'S3Object': {
                        'Bucket': self.storage.bucket_name,
                        'Name': filename
                    }
                }
            )
            
            print(f"Textract response received. Blocks count: {len(response['Blocks'])}")
            
            text_lines = []
            for block in response['Blocks']:
                if block['BlockType'] == 'LINE' and block['Confidence'] >= min_confidence:
                    text_lines.append(block['Text'])
                    print(f"Line detected (confidence: {block['Confidence']:.1f}): {block['Text']}")
            
            extracted_text = ' '.join(text_lines)
            print(f"Text extraction complete. Total lines: {len(text_lines)}, Total length: {len(extracted_text)}")
            return extracted_text
        except Exception as e:
            print(f"ERROR in Textract extraction: {str(e)}")
            raise