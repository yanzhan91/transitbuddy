import re
import requests
import json
from datetime import datetime, timedelta, timezone
import math

if __name__ == '__main__':
    from agency import Agency
else:
    from agencies.agency import Agency

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

    def check_bus(self, bus_id, _, stop_id):
        secrets = self._get_secret()
        key = json.loads(secrets)['transitbuddy_cta_train_api_key']
        response = requests.get('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?'
            f'key={key}&rt={bus_id}&stpid={stop_id}&outputType=json')

        minutes = []

        traintime_response = response.json()['ctatt']

        if ('errCd' in traintime_response and traintime_response['errCd'] != '0') \
            or 'eta' not in traintime_response:
            return minutes, 'train', train_color_map[bus_id], stop_id, None

        predictions = traintime_response['eta']

        if len(predictions) == 0:
            return minutes, 'train', train_color_map[bus_id], stop_id, None

        for prdt in predictions:
            # print(f"{prdt['arrT']} - {prdt['staNm']} - {prdt['rt']} - {prdt['destNm']}")
            minute = self.__get_predictions(prdt)
            if minute >= 0:
                minutes.append(minute)
            if len(minutes) == 2:
                break

        station = re.sub('[/-]', ' and ', predictions[0]['staNm'])
        
        return minutes, 'train', train_color_map[bus_id], '', station

    def __get_predictions(self, prdt):
        predicted_time = datetime.strptime(prdt['arrT'] + ' -0500', '%Y-%m-%dT%H:%M:%S %z')
        now = datetime.now(tz=timezone(timedelta(hours=-5)))
        time_delta = (predicted_time - now)
        total_seconds = time_delta.total_seconds()
        return math.floor(total_seconds / 60)

if __name__ == '__main__':
    agency = ChicagoCTATrain()
    # print(agency.get_bus('', '1'))
    print(agency.check_bus('Blue', '30375'))
