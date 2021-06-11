if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import boto3

from models.preset import Preset

def get_bus(token, preset=1):
    username = __get_username(token)
    # username = 'test'

    client = boto3.client('dynamodb', region_name='us-east-2')
    response = client.get_item(
        Key={
            "userId": {
                "S": username,
            },
            "presetId": {
                "N": str(preset)
            }
        },
        TableName='transitbuddy_presets-dev',
    )

    try:
        return Preset(response['Item'])
    except (KeyError, IndexError):
        return None

def __get_username(token):
    client = boto3.client('cognito-idp', region_name='us-east-2')
    return client.get_user(AccessToken=token)['Username']

if __name__ == '__main__':
    print(get_bus(None))
    