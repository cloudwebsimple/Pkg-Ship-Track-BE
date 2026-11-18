from chalice import Chalice, Response
from chalicelib.text_detection_service import TextDetectionService
from chalicelib.entity_recognition_service import EntityRecognitionService
from chalicelib.storage_service import StorageService
from chalicelib.database_service import DatabaseService
import base64
import json

app = Chalice(app_name='pkg-ship-track')
app.debug = True

# Configure CORS for all routes
app.cors = True

# Services
storage = StorageService('pkg-ship-track-images-186814813507-us')
text_detector = TextDetectionService(storage)
entity_recognizer = EntityRecognitionService()
database = DatabaseService('TextDetectionTable')

@app.route('/upload', methods=['POST'], cors=True)
def upload_and_process():
    """Upload image, detect text, extract entities, and store results"""
    print("=== Starting upload and process request ===")
    try:
        data = json.loads(app.current_request.raw_body)
        print(f"Request data keys: {list(data.keys())}")
        
        file_bytes = base64.b64decode(data['file_data'])
        filename = data['filename']
        user_id = data['user_id']
        comment = data.get('comment', '')
        
        print(f"Processing file: {filename} for user: {user_id}")
        print(f"File size: {len(file_bytes)} bytes")
        print(f"Comment: {comment}")
        
        # Upload to S3
        print("Uploading to S3...")
        image_url = storage.upload(file_bytes, filename)
        print(f"S3 upload complete: {image_url}")
        
        # Detect text
        print("Starting text detection...")
        detected_text = text_detector.extract_text(filename)
        print(f"Text detection complete. Length: {len(detected_text)}")
        
        # Extract entities
        print("Starting entity extraction...")
        entities = entity_recognizer.extract_entities(detected_text)
        print(f"Entity extraction complete: {entities}")
        
        # Store in database
        print("Storing in database...")
        record_id = database.store_record(user_id, filename, detected_text, entities, image_url, comment)
        print(f"Database storage complete. Record ID: {record_id}")
        
        result = {
            'record_id': record_id,
            'detected_text': detected_text,
            'entities': entities,
            'image_url': image_url
        }
        print(f"=== Request completed successfully ===")
        return result
    except Exception as e:
        print(f"ERROR in upload_and_process: {str(e)}")
        return {'error': str(e)}

@app.route('/records/{user_id}', methods=['GET'], cors=True)
def get_records(user_id):
    """Get all text detection records for a user"""
    print(f"Getting records for user: {user_id}")
    try:
        records = database.get_user_records(user_id)
        print(f"Found {len(records)} records for user {user_id}")
        return records
    except Exception as e:
        print(f"ERROR in get_records: {str(e)}")
        return {'error': str(e)}

@app.route('/records/{user_id}/{record_id}', methods=['GET'], cors=True)
def get_record(user_id, record_id):
    """Get specific text detection record"""
    print(f"Getting record {record_id} for user {user_id}")
    try:
        record = database.get_record(user_id, record_id)
        if record:
            print(f"Record found: {record_id}")
        else:
            print(f"Record not found: {record_id}")
        return record
    except Exception as e:
        print(f"ERROR in get_record: {str(e)}")
        return {'error': str(e)}
    
@app.route('/test', methods=['POST'], cors=True)
def handler():
    return Response(
        body={'message': 'ok'},
        headers={
            'Access-Control-Allow-Origin': app.current_request.headers.get('origin', '*'),
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Credentials': 'true'
        },
        status_code=200
    )