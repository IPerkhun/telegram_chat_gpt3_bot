import boto3
from config import ConfigManager

aws_access_key_id = ConfigManager().get('default', 'DYNAMO_DB_AWS_ACCESS_KEY_ID')
aws_secret_access_key = ConfigManager().get('default', 'DYNAMO_DB_AWS_SECRET_SECRET_KEY')
region = ConfigManager().get('default', 'AWS_REGION')
# Create a DynamoDB client with your credentials
dynamodb = boto3.client('dynamodb',
                        region_name=region,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)

# test connection
try:
    response = dynamodb.list_tables()
    print(response)
except Exception as e:
    print(e)
