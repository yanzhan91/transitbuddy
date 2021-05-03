import requests
import os

def check_bus(bus_id, stop_id):
    response = requests.get('http://www.ctabustracker.com/bustime/api/v2/getpredictions?'
                            'key=%s&rt=%s&stpid=%s&top=2&format=json&top=2' % (os.environ['api_key'], bus_id, stop_id))

    minutes = []

    bustime_response = response.json()['bustime-response']

    if 'error' in bustime_response:
        return minutes, None

    predictions = bustime_response['prd']

    for prdt in predictions:
        minutes.append(prdt['prdctdn'])

    return minutes, predictions[0]['stpnm']

if __name__ == '__main__':
    os.environ['api_key'] = 'api_key'
    print(check_bus('151', '1108'))
