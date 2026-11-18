import boto3
import uuid
from datetime import datetime

class DatabaseService:
    def __init__(self, table_name):
        self.dynamodb = boto3.client('dynamodb', region_name='us-east-1')
        self.table_name = table_name

    def store_record(self, user_id, filename, detected_text, entities, image_url, comment=''):
        """Store text detection record with extracted entities in DynamoDB"""
        record_id = str(uuid.uuid4())
        print(f"Storing record in DynamoDB: {record_id} for user {user_id}")
        print(f"Entities to store: {entities}")
        
        try:
            self.dynamodb.put_item(
                TableName=self.table_name,
                Item={
                    'user_id': {'S': user_id},
                    'record_id': {'S': record_id},
                    'filename': {'S': filename},
                    'detected_text': {'S': detected_text},
                    'first_name': {'S': entities.get('first_name', '')},
                    'last_name': {'S': entities.get('last_name', '')},
                    'unit_number': {'S': entities.get('unit_number', '')},
                    'full_address': {'S': entities.get('full_address', '')},
                    'tracking_number': {'S': entities.get('tracking_number', '')},
                    'comment': {'S': comment},
                    'image_url': {'S': image_url},
                    'created_at': {'S': datetime.utcnow().isoformat()}
                }
            )
            print(f"DynamoDB record stored successfully: {record_id}")
            return record_id
        except Exception as e:
            print(f"ERROR storing record in DynamoDB: {str(e)}")
            raise

    def get_user_records(self, user_id):
        """Get all records for a user"""
        print(f"Querying DynamoDB for user records: {user_id}")
        try:
            response = self.dynamodb.query(
                TableName=self.table_name,
                KeyConditionExpression='user_id = :user_id',
                ExpressionAttributeValues={':user_id': {'S': user_id}}
            )
            
            records = []
            for item in response.get('Items', []):
                records.append({
                    'record_id': item['record_id']['S'],
                    'filename': item['filename']['S'],
                    'detected_text': item['detected_text']['S'],
                    'first_name': item.get('first_name', {}).get('S', ''),
                    'last_name': item.get('last_name', {}).get('S', ''),
                    'unit_number': item.get('unit_number', {}).get('S', ''),
                    'full_address': item.get('full_address', {}).get('S', ''),
                    'tracking_number': item.get('tracking_number', {}).get('S', ''),
                    'comment': item.get('comment', {}).get('S', ''),
                    'image_url': item['image_url']['S'],
                    'created_at': item['created_at']['S']
                })
            
            print(f"Retrieved {len(records)} records for user {user_id}")
            return records
        except Exception as e:
            print(f"ERROR querying user records: {str(e)}")
            raise

    def get_record(self, user_id, record_id):
        """Get specific record"""
        print(f"Getting specific record: {record_id} for user {user_id}")
        try:
            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    'user_id': {'S': user_id},
                    'record_id': {'S': record_id}
                }
            )
            
            if 'Item' not in response:
                print(f"Record not found: {record_id}")
                return None
                
            item = response['Item']
            record = {
                'record_id': item['record_id']['S'],
                'filename': item['filename']['S'],
                'detected_text': item['detected_text']['S'],
                'first_name': item.get('first_name', {}).get('S', ''),
                'last_name': item.get('last_name', {}).get('S', ''),
                'unit_number': item.get('unit_number', {}).get('S', ''),
                'full_address': item.get('full_address', {}).get('S', ''),
                'tracking_number': item.get('tracking_number', {}).get('S', ''),
                'comment': item.get('comment', {}).get('S', ''),
                'image_url': item['image_url']['S'],
                'created_at': item['created_at']['S']
            }
            print(f"Record retrieved successfully: {record_id}")
            return record
        except Exception as e:
            print(f"ERROR getting specific record: {str(e)}")
            raise