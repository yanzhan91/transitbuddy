if __name__ == '__main__':
    import os
    import sys

    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(BASE_PATH)

import requests
from datetime import datetime, timezone, timedelta
import math

from agencies.agency import Agency
from models.preset import Preset

class ChicagoPaceBus(Agency):

    def check_bus(self, preset):

        response = requests.post(
            'https://tmweb.pacebus.com/TMWebWatch/Arrivals.aspx/getStopTimes',
            json={
                "routeID": preset.route_id, 
                "directionID": preset.direction_id, 
                "stopID": preset.stop_id, 
                "tpID": 0, 
                "useArrivalTimes": False
            }
        )

        minutes = []

        bustime_response = response.json()['d']['routeStops']

        if len(bustime_response) == 0:
            return self.__create_response(minutes, preset)

        stops = bustime_response[0]['stops']

        if len(stops) == 0:
            return self.__create_response(minutes, preset)

        predictions = stops[0]['crossings']

        if not predictions or len(predictions) == 0:
            return self.__create_response(minutes, preset)

        for prdt in predictions:
            minute = self.__get_predictions(prdt)
            if minute >= 0:
                minutes.append(minute)
            if len(minutes) == 2:
                break

        return self.__create_response(minutes, preset)

    def __get_predictions(self, prdt):
        now = datetime.now(tz=timezone(timedelta(hours=-5)))
        predicted_time = datetime.strptime(
            f"{prdt['predTime'] if prdt['predTime'][0] == '1' else ('0' + prdt['predTime'])} "
            f"{prdt['predPeriod'].upper()} -0500", '%I:%M %p %z')
        predicted_time = predicted_time.replace(year=now.year, month=now.month, \
            day=now.day + (1 if now.time() > predicted_time.time() else 0))
        time_delta = (predicted_time - now)
        total_seconds = time_delta.total_seconds()
        return math.floor(total_seconds / 60)

    def __create_response(self, minutes, preset):
        route = preset.route_name.split(' - ')[0]
        direction = preset.direction_name
        stop = preset.stop_name
        return minutes, f"Pace bus {route} heading {direction} at stop {stop}"


if __name__ == '__main__':
    agency = ChicagoPaceBus()
    print(agency.check_bus(Preset.create_test_preset(
        {
            "routeId": "8",
            "routeName": "208 - Golf Road",
            "directionId": "1",
            "directionName": "East",
            "stopId": "9453",
            "stopName": "1111 Plaza Dr"
        }
    )))