import requests
import json

if __name__ == '__main__':
    from agency import Agency
else:
    from agencies.agency import Agency

class UMichMagicBus(Agency):

    def check_bus(self, bus_id, _, stop_id):
        key = json.loads(self._get_secret())['umich_magic_bus_api_key']
        response = requests.get('https://mbus.ltp.umich.edu/bustime/api/v3/getpredictions?'
            f'key={key}&rt={bus_id}&stpid={stop_id}&top=2&format=json')

        minutes = []

        bustime_response = response.json()['bustime-response']

        if 'error' in bustime_response:
            return minutes, 'bus', bus_id, stop_id, ''

        predictions = bustime_response['prd']

        if len(predictions) == 0:
            return minutes, 'bus', bus_id, stop_id, ''

        for prdt in predictions:
            minutes.append('0' if prdt['prdctdn'] == 'DUE' else prdt['prdctdn'])

        station = predictions[0]['stpnm']

        if station:
            station = station.replace('&', 'and')

        return minutes, 'bus', bus_id, stop_id, station

if __name__ == '__main__':
    agency = UMichMagicBus()
    # print(get_bus('', '1'))
    
    print(agency.check_bus('CC', None, 'C206'))