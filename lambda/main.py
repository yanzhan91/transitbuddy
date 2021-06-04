import logging
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.view_resolvers import FileSystemTemplateLoader
from ask_sdk_jinja_renderer import JinjaTemplateRenderer

from agencies.chicago_cta_bus import ChicagoCTABus
from agencies.chicago_cta_train import ChicagoCTATrain
from agencies.chicago_pace_bus import ChicagoPaceBus

import utils

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    return respond(handler_input, 'launch_response')

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_request_handler(handler_input):
    return respond(handler_input, 'launch_response')

@sb.request_handler(
    can_handle_func=lambda handler_input:
        is_intent_name("AMAZON.CancelIntent")(handler_input) or
        is_intent_name("AMAZON.StopIntent")(handler_input))
def cancel_request_handler(handler_input):
    speech_text = "Ok!"
    handler_input.response_builder.speak(speech_text)
    return handler_input.response_builder.response

@sb.exception_handler(can_handle_func=lambda i, e: True)
def exception_handler(handler_input, exception):
    logger.error(exception, exc_info=True)

    speech = "Sorry, I didn't understand that. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    return respond(handler_input, 'fallback_response')

@sb.request_handler(can_handle_func=is_intent_name("CheckBusIntent"))
def check_bus_handler(handler_input):
    return respond(handler_input, 'account_linking_response')

@sb.request_handler(can_handle_func=is_intent_name("GetBusIntent"))
def get_bus_handler(handler_input):
    preset_id = get_slot_value(handler_input, 'preset_id', '1')
    logger.info(f'Getting Bus at preset {preset_id}...')

    user = handler_input.request_envelope.context.system.user
    if user.access_token:
        token = user.access_token;
        return get_bus(handler_input, token, preset_id)
    else:
        return respond(handler_input, 'account_linking_response')

@sb.request_handler(can_handle_func=is_intent_name("SetBusIntent"))
def set_bus_handler(handler_input):
    return respond(handler_input, 'account_linking_response')

def get_slot_value(handler_input, key, default=None):
    slots = handler_input.request_envelope.request.intent.slots
    slot = slots[key]
    if slot.resolutions:
        matches = slot.resolutions.to_dict()['resolutions_per_authority'][0]['values']
        # status_code = slot.resolutions.to_dict()['resolutions_per_authority'][0]['status']['code']
        if not matches or len(matches) == 0:
            slot_value = slot.value
        return matches[0]['value']['name']
    else:
        slot_value =  slot.value
    
    if not slot_value:
        return default
    else:
        return slot_value

def respond(handler_input, response_file, data_map={'test': 'test'}):
    return handler_input.generate_template_response(response_file, data_map, file_ext='jinja')

def get_bus(handler_input, token, preset_id):
    logger.info(f'Getting Bus at preset {preset_id}...')
    agency, bus_id, direction_id, stop_id = utils.get_bus(token, preset_id)
    logger.info(f'Bus retrieved was {bus_id} at {stop_id}')

    if not bus_id or not stop_id:
        return respond(handler_input, "no_preset_response", {
            'preset_id': preset_id
        })
    return check_bus(handler_input, agency, bus_id, direction_id, stop_id, preset_id)

def check_bus(handler_input, agency, bus_id, direction_id, stop_id, preset_id = None, notify_account_linking = False):
    minutes, type, bus, stop, station = __get_agency(agency).check_bus(bus_id, direction_id, stop_id)

    logger.info('Minutes received: %s' % minutes)
    if len(minutes) == 0:
        return respond(handler_input, 'no_bus_response', {
            'bus_id': bus,
            'stop_id': stop,
            'with_preset': f'At preset {preset_id}, <break time=\\"200ms\\"/> ' if preset_id else ''
        })
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away' % minute)

    notify_account_linking = notify_account_linking and random.randint(1,5) == 5

    return respond(handler_input, "bus_time_response", {
        'type': type,
        'bus_id': bus,
        'stop_id': stop,
        'minutes': ' <break time=\\"200ms\\"/> and '.join(minute_strings),
        'card_minutes': ' and '.join(minute_strings),
        'stop_name': station,
        'with_preset': f'At preset {preset_id}, <break time=\\"200ms\\"/> ' if preset_id else '',
        'account_linking': 'For more simplicity, you can create presets to more easily get your bus times. '
            'Check the alexa app for details in the Transit Buddy skills page.' if notify_account_linking else ''
    })

def __get_agency(agency):
    if agency == 'Chicago CTA Train':
        return ChicagoCTATrain()
    elif agency == 'Chicago Pace Bus':
        return ChicagoPaceBus()
    else:
        return ChicagoCTABus()

sb.add_loader(FileSystemTemplateLoader(dir_path="templates", encoding='utf-8'))
sb.add_renderer(JinjaTemplateRenderer())

handler = sb.lambda_handler()

if __name__ == '__main__':
    print(utils.get_bus('eyJraWQiOiI4TElDRXhvV2R5NWNzQUV6TlB2dkp6N3dlbGE5djdwRVFhRE5FVkphT05vPSIsImFsZyI6IlJTMjU2In0.eyJzdWIiOiI4OGRlMDNhZC0yNDYyLTQxZjAtOGEzYS1iN2EyZjc0MzY3YzkiLCJldmVudF9pZCI6IjAwNzVmZTNjLTBhOTItNDNhNi1iZjFiLWQ1NjJiMGI3ZTg1MSIsInRva2VuX3VzZSI6ImFjY2VzcyIsInNjb3BlIjoiYXdzLmNvZ25pdG8uc2lnbmluLnVzZXIuYWRtaW4gb3BlbmlkIHByb2ZpbGUiLCJhdXRoX3RpbWUiOjE2MjE4MzkyOTMsImlzcyI6Imh0dHBzOlwvXC9jb2duaXRvLWlkcC51cy1lYXN0LTIuYW1hem9uYXdzLmNvbVwvdXMtZWFzdC0yX2pnbXJjOGxLdCIsImV4cCI6MTYyMjc3OTAxOSwiaWF0IjoxNjIyNzc1NDE5LCJ2ZXJzaW9uIjoyLCJqdGkiOiI4N2M3NmZhMy03NjkxLTQwMTItYTljMS1iYWYyZWNkNTEyZDUiLCJjbGllbnRfaWQiOiI1bGsyZnZtdDdlcGRndmg3dmk2MzB0djhmMiIsInVzZXJuYW1lIjoiODhkZTAzYWQtMjQ2Mi00MWYwLThhM2EtYjdhMmY3NDM2N2M5In0.sUmMFo3Sq06Kb67DMPz63sVrLBOYQzIxxAZkbDTjJ8DaQLb4YbGPJDnVWXYeogAc3_W-TD-7M1Xr1FKkpeoFdZFFM54A43q8j0qFr4m7rvPgpte55PkNT06DVbn8gv8BhIU3UlWlv8Mc6qs2YaEqmzVWXIAjNcxGNBHHE2s37jEJ3aSjvxsN6QhhI5W6gHaYI2RfeN-EfBa8vUVhIIuGNZsYD7TloO8H4oY7aV37EvDI_lH9VRc7z7YPZygNF2vlcrIyXaOhGavxS844zgaKa0wjhZxcBJT1QQufaSBWZjMZeDhlPtKzYm7Z9q4eMJ2K1y3RFZ-W3qz3cZvy3Oy7eg', preset=10))
    # print(__get_agency("Blue").check_bus("Blue", "30375"))
    
