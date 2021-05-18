import boto3

def get_bus(token, preset=1):
    username = _get_username(token)

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
        item = response['Item']
        return item['routeId']['S'], item['stopId']['S']
    except (KeyError, IndexError):
        return None, None

def _get_username(token):
    client = boto3.client('cognito-idp', region_name='us-east-2')
    return client.get_user(AccessToken=token)['Username']

if __name__ == '__main__':
    print(get_bus('', '1'))