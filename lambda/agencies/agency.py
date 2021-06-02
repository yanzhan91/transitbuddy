import base64
from abc import abstractmethod

import boto3
from botocore.exceptions import ClientError


class Agency:
    @abstractmethod
    def check_bus(self, bus_id, direction_id, stop_id):
        pass

    @abstractmethod
    def get_bus(self, token, preset=1):
        pass

    def _get_secret(self):
        secret_name = "transitbuddy/secrets"
        region_name = "us-east-2"

        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=region_name
        )

        try:
            get_secret_value_response = client.get_secret_value(
                SecretId=secret_name
            )
        except ClientError as e:
            raise e
        else:
            if 'SecretString' in get_secret_value_response:
                return get_secret_value_response['SecretString']
            else:
                return base64.b64decode(get_secret_value_response['SecretBinary'])
