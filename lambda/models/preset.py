class Preset:
    def __init__(self, item):
        self.preset_id = item["presetId"]['N']
        self.route_id = item["routeId"]['S']
        self.route_name = item["routeName"]['S']
        self.direction_id = item["directionId"]['S'] if 'directionId' in item else None
        self.direction_name = item["directionName"]['S'] if 'directionName' in item else None
        self.stop_id = item["stopId"]['S']
        self.stop_name = item["stopName"]['S']
        self.agency_name = item["agency"]['S']

    def __str__(self):
        return f"{self.preset_id} - " \
            f"{self.route_id} ({self.route_name}) - " \
            f"{self.direction_id} ({self.direction_name}) - " \
            f"{self.stop_id} ({self.stop_name}) - " \
            f"{self.agency_name}"

    @classmethod
    def create_test_preset(_, params):
        return Preset({
            "presetId": {"N": params["presetId"] if 'presetId' in params else None},
            "routeId": {"S": params["routeId"] if 'routeId' in params else None},
            "routeName": {"S": params["routeName"] if 'routeName' in params else None},
            "directionId": {"S": params["directionId"] if 'directionId' in params else None},
            "directionName": {"S": params["directionName"] if 'directionName' in params else None},
            "stopId": {"S": params["stopId"] if 'stopId' in params else None},
            "stopName": {"S": params["stopName"] if 'stopName' in params else None},
            "agency": {"S": params["agency"] if 'agency' in params else None},
        })