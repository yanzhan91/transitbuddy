if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import requests
import json
from datetime import datetime, timedelta, timezone
import math

from agencies.agency import Agency
from models.preset import Preset

train_color_map = {
    "Red" : "red",
    "Blue" : "blue",
    "G" : "green",
    "Brn" : "brown",
    "P" : "purple",
    "Y" : "yellow",
    "Pink" : "pink",
    "Org" : "orange",
}

class ChicagoCTATrain(Agency):

    def check_bus(self, preset):
        secrets = self._get_secret()
        key = json.loads(secrets)['transitbuddy_cta_train_api_key']
        response = requests.get('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?'
            f'key={key}&rt={preset.route_id}&stpid={preset.stop_id}&outputType=json')

        minutes = []

        traintime_response = response.json()['ctatt']

        if ('errCd' in traintime_response and traintime_response['errCd'] != '0') \
            or 'eta' not in traintime_response:
            return self.__create_response(minutes, preset)

        for prdt in traintime_response['eta']:
            minute = self.__get_predictions(prdt)
            if minute >= 0:
                minutes.append(minute)
            if len(minutes) == 2:
                break

        return self.__create_response(minutes, preset)

    def __get_predictions(self, prdt):
        predicted_time = datetime.strptime(prdt['arrT'] + ' -0500', '%Y-%m-%dT%H:%M:%S %z')
        now = datetime.now(tz=timezone(timedelta(hours=-5)))
        time_delta = (predicted_time - now)
        total_seconds = time_delta.total_seconds()
        return math.floor(total_seconds / 60)

    def __create_response(self, minutes, preset):
        route = preset.route_name.split(' ')
        direction = preset.direction_name
        stop = preset.stop_name
        return minutes, f"CTA train {direction} {route[0]} {route[1]} at stop {stop}"

if __name__ == '__main__':
    agency = ChicagoCTATrain()
    print(agency.check_bus(Preset.create_test_preset(
        {
            "routeId": "Red",
            "routeName": "Red Line (Howard-95th/Dan Ryan)",
            "directionId": "1",
            "directionName": "Howard-bound",
            "stopId": "30177",
            "stopName": "63rd",
        }
    )))
