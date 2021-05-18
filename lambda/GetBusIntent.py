import boto3
from boto3.dynamodb.conditions import Key

def get_bus(user_id, preset):
    user_table = boto3.resource('dynamodb').Table('TransitBuddy_Users')
    response = user_table.query(
        KeyConditionExpression=Key('user_id').eq(user_id),
        Limit=1
    )

    try:
        user = response['Items'][0]
        user = user[f'preset {preset}']
    except (KeyError, IndexError):
        return None, None

    return user['bus_id'], user['stop_id']

def get_bus_v2(token, preset=1):
    username = _get_username(token)

    client = boto3.client('dynamodb')
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
    return client.get_user(AccessToken=token)['username']

if __name__ == '__main__':
    print(get_bus('123', '1'))