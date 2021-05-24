import requests
import json

if __name__ == '__main__':
    from agency import Agency
else:
    from agencies.agency import Agency

class ChicagoCTABus(Agency):

    def check_bus(self, bus_id, stop_id):
        key = json.loads(self._get_secret())['transitbuddy_cta_bus_api_key']
        response = requests.get('http://www.ctabustracker.com/bustime/api/v2/getpredictions?'
            f'key={key}&rt={bus_id}&stpid={stop_id}&top=2&format=json')

        minutes = []

        bustime_response = response.json()['bustime-response']

        if 'error' in bustime_response:
            return minutes, None

        predictions = bustime_response['prd']

        if len(predictions) == 0:
            return minutes, None

        for prdt in predictions:
            minutes.append('0' if prdt['prdctdn'] == 'DUE' else prdt['prdctdn'])

        station = predictions[0]['stpnm']

        if station:
            station = station.replace('&', 'and')

        return minutes, station

if __name__ == '__main__':
    agency = ChicagoCTABus()
    # print(get_bus('', '1'))
    
    print(agency.check_bus('151', '1108'))