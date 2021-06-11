if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import requests
import json  

from agencies.agency import Agency
from models.preset import Preset

class ChicagoCTABus(Agency):

    def check_bus(self, preset):
        key = json.loads(self._get_secret())['transitbuddy_cta_bus_api_key']
        response = requests.get('http://www.ctabustracker.com/bustime/api/v2/getpredictions?'
            f'key={key}&rt={preset.route_id}&stpid={preset.stop_id}&top=2&format=json')

        minutes = []

        bustime_response = response.json()['bustime-response']

        if 'error' in bustime_response:
            return self.__create_response(minutes, preset)

        for prdt in bustime_response['prd']:
            minutes.append('0' if prdt['prdctdn'] == 'DUE' else prdt['prdctdn'])

        return self.__create_response(minutes, preset)

    def __create_response(self, minutes, preset):
        route = preset.route_id
        direction = preset.direction_name
        stop = preset.stop_name
        return minutes, f"CTA bus {route} {direction} at stop {stop}"

if __name__ == '__main__':
    agency = ChicagoCTABus()
    print(agency.check_bus(Preset.create_test_preset(
        {
            "agency": "Chicago CTA Bus",
            "directionId": "Northbound",
            "directionName": "Northbound",
            "presetId": 3,
            "routeId": "2",
            "routeName": "2 - Hyde Park Express",
            "stopId": "755",
            "stopName": "Illinois & Peshtigo",
            "userId": "88de03ad-2462-41f0-8a3a-b7a2f74367c9"
        }
    )))