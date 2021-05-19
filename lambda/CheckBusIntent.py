import requests
import base64
from botocore.exceptions import ClientError
import json
import boto3

def get_secret():
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

def check_bus(bus_id, stop_id):
    key = json.loads(get_secret())['transitbuddy_cta_bus_api_key']
    response = requests.get('http://www.ctabustracker.com/bustime/api/v2/getpredictions?'
                            'key=%s&rt=%s&stpid=%s&top=2&format=json&top=2' % (key, bus_id, stop_id))

    minutes = []

    bustime_response = response.json()['bustime-response']

    if 'error' in bustime_response:
        return minutes, None

    predictions = bustime_response['prd']

    for prdt in predictions:
        minutes.append(prdt['prdctdn'])

    return minutes, predictions[0]['stpnm']

if __name__ == '__main__':
    print(check_bus('X98', '17037'))
