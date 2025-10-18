import boto3
import base64
import hmac
import hashlib
from botocore.exceptions import ClientError
from app.core.config import settings

class CognitoService:
    def __init__(self):
        self.client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        self.user_pool_id = settings.COGNITO_USER_POOL_ID
        self.client_id = settings.COGNITO_APP_CLIENT_ID
        self.client_secret = settings.COGNITO_APP_CLIENT_SECRET
    
    def _calculate_secret_hash(self, username):
        if not self.client_secret:
            return None
            
        message = username + self.client_id
        dig = hmac.new(
            self.client_secret.encode('utf-8'),
            msg=message.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        return base64.b64encode(dig).decode()
    
    def sign_up(self, username, password, email, user_attributes):
        try:
            secret_hash = self._calculate_secret_hash(username)
            
            kwargs = {
                'ClientId': self.client_id,
                'Username': username,
                'Password': password,
                'UserAttributes': user_attributes
            }
            
            if secret_hash:
                kwargs['SecretHash'] = secret_hash
                
            response = self.client.sign_up(**kwargs)
            return response
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
    
    def confirm_sign_up(self, username, confirmation_code):
        try:
            secret_hash = self._calculate_secret_hash(username)
            
            kwargs = {
                'ClientId': self.client_id,
                'Username': username,
                'ConfirmationCode': confirmation_code
            }
            
            if secret_hash:
                kwargs['SecretHash'] = secret_hash
                
            response = self.client.confirm_sign_up(**kwargs)
            return response
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
    
    def initiate_auth(self, username, password):
        try:
            secret_hash = self._calculate_secret_hash(username)
            
            kwargs = {
                'ClientId': self.client_id,
                'AuthFlow': 'USER_PASSWORD_AUTH',
                'AuthParameters': {
                    'USERNAME': username,
                    'PASSWORD': password
                }
            }
            
            if secret_hash:
                kwargs['AuthParameters']['SECRET_HASH'] = secret_hash
                
            response = self.client.initiate_auth(**kwargs)
            return response
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
    
    def get_user(self, access_token):
        try:
            response = self.client.get_user(AccessToken=access_token)
            return response
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])
    
    def admin_add_user_to_group(self, username, group_name):
        try:
            response = self.client.admin_add_user_to_group(
                UserPoolId=self.user_pool_id,
                Username=username,
                GroupName=group_name
            )
            return response
        except ClientError as e:
            raise Exception(e.response['Error']['Message'])