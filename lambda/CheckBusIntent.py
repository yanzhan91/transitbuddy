import requests
import os

def check_bus(agency_id, bus_id, stop_id):
    if agency_id == 'cta bus':
        return check_cta_bus(bus_id, stop_id)
    else:
        return check_cta_train(bus_id, stop_id)

def check_cta_train(bus_id, stop_id):
    # https://tmweb.pacebus.com/TMWebWatch/Arrivals.aspx/getStopTimes
    # {routeID: 190,	directionID: 3,	stopID:	29359,	tpID:	0, useArrivalTimes:	false}
    # response = requests.post('https://tmweb.pacebus.com/TMWebWatch/Arrivals.aspx/getStopTimes', \
    #     params={'routeID': bus_id, "stopID": stop_id, "directionID": 3, "tpID": 0, "useArrivalTimes": False}, \
    #     headers={"Accept": "application/json, text/javascript", "Cookie": "route=190; direction=3; stop=29359_0; _gcl_au=1.1.951058917.1620193975; _ga=GA1.2.985980463.1620193975; ASP.NET_SessionId=z0tfmbyjwyviowtwbbouoi11; __session:0.3043459776697821:enableLogin=true; _gid=GA1.2.715527290.1620282119; __session:0.3043459776697821:=https:; _gat_UA-1091731-1=1; __session:0.8966047113832565:=https:; __session:0.8966047113832565:enableLogin=true"})
    # print(response.status_code)
    response = requests.get('http://lapi.transitchicago.com/api/1.0/ttarrivals.aspx?'
                            'key=4f4ae2bcec6e493e869f1f85bee457fd&mapid=40380')
    print(response.content)
    # print(response.json())

def check_cta_bus(bus_id, stop_id):
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
    check_cta_train('190', '29359')
