if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import boto3

from models.preset import Preset

def get_bus(username, preset=1):
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

    return Preset(response['Item']) if 'Item' in response else None

if __name__ == '__main__':
    print(get_bus(None))
    