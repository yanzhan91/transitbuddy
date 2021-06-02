import boto3

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
        item = response['Item']
        return item['routeId']['S'], \
            item['directionId']['S'] if 'directionId' in item else None, item['stopId']['S']
    except (KeyError, IndexError):
        return None, None, None

def __get_username(token):
    client = boto3.client('cognito-idp', region_name='us-east-2')
    return client.get_user(AccessToken=token)['Username']