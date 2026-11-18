# Pkg-Ship-Track

Text detection and entity extraction from shipping labels using AWS services.

## Features
- Upload images and extract text using AWS Textract
- Extract entities: first name, last name, unit number, full address, tracking number
- Add custom comments/notes
- Store structured data in DynamoDB

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Deploy Infrastructure
```bash
./deploy-infra.sh
```

### 3. Deploy Application
```bash
chalice deploy --stage dev
```

## API Endpoints

### Upload and Process Image
```
POST /upload
{
  "file_data": "base64_encoded_image",
  "filename": "image.jpg", 
  "user_id": "user123",
  "comment": "Optional note"
}
```

### Get User Records
```
GET /records/{user_id}
```

### Get Specific Record
```
GET /records/{user_id}/{record_id}
```

### Response
```
{
  "record_id": "89b2412a-4bf6-4dfd-8191-0e2161e6e626",
  "detected_text": "YYZ1 7.0 Lbs 08/24 DON8 Linda Cui 33 University Avenue Suite 808 M5J 2S7 Toronto , Ontario Canada LIQUID TBC176747891009 DON8 CYCLE 1 Q7C4S3chG Q7C4S3chG YYZ7 & ON8",
  "entities": {
    "first_name": "Linda",
    "last_name": "Cui",
    "unit_number": "808",
    "full_address": "",
    "tracking_number": "TBC176747891009"
  },
  "image_url": "https://pkg-ship-track-images-186814813507-us.s3.amazonaws.com/IMG_3223.jpg"
}
```

## Architecture
- **Chalice**: Serverless Python framework
- **AWS Textract**: Text detection from images
- **AWS Comprehend**: Entity recognition
- **S3**: Image storage
- **DynamoDB**: Structured data storage
- **CDK**: Infrastructure as code