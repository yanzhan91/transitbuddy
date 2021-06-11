if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import requests
import json

from agencies.agency import Agency
from models.preset import Preset

class UMichMagicBus(Agency):

    def check_bus(self, preset):
        key = json.loads(self._get_secret())['umich_magic_bus_api_key']
        response = requests.get('https://mbus.ltp.umich.edu/bustime/api/v3/getpredictions?'
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
        return minutes, f"Magic Bus {route} {direction} at stop {stop}"

if __name__ == '__main__':
    agency = UMichMagicBus()
    print(agency.check_bus(Preset.create_test_preset(
        {
            "routeId": "OXM",
            "routeName": "Oxford-Markley Loop",
            "directionId": "NORTHBOUND",
            "directionName": "NORTHBOUND",
            "stopId": "C206",
            "stopName": "Oxford Housing",
        }
    )))