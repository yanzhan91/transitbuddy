import requests
from datetime import datetime, timezone, timedelta
import math

if __name__ == '__main__':
    from agency import Agency
else:
    from agencies.agency import Agency

class ChicagoPaceBus(Agency):

    def check_bus(self, bus_id, direction_id, stop_id):
        response = requests.post(
            'https://tmweb.pacebus.com/TMWebWatch/Arrivals.aspx/getStopTimes',
            json={
                "routeID": bus_id, 
                "directionID": direction_id, 
                "stopID": "21440", 
                "tpID": 0, 
                "useArrivalTimes": False
            }
        )

        minutes = []

        bustime_response = response.json()['d']['routeStops']

        if len(bustime_response) == 0:
            return minutes, 'bus', bus_id, stop_id, ''

        stops = bustime_response[0]['stops']

        if len(stops) == 0:
            return minutes, 'bus', bus_id, stop_id, ''

        predictions = stops[0]['crossings']

        if not predictions or len(predictions) == 0:
            return minutes, 'bus', bus_id, stop_id, ''

        for prdt in predictions:
            minute = self.__get_predictions(prdt)
            if minute >= 0:
                minutes.append(minute)
            if len(minutes) == 2:
                break

        return minutes, 'bus', bus_id, stop_id, None

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

if __name__ == '__main__':
    agency = ChicagoPaceBus()
    print(agency.check_bus('23', '1', '21440'))