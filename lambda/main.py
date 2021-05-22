import logging
import random

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name

import CheckBusIntent
import GetBusIntent

from ask_sdk_core.view_resolvers import FileSystemTemplateLoader
from ask_sdk_jinja_renderer import JinjaTemplateRenderer

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
    bus_id = None
    stop_id = None

    try:
        bus_id = get_slot_value(handler_input, 'bus_id')
        stop_id = get_slot_value(handler_input, 'stop_id')
    except:
        pass

    if not bus_id or not stop_id:
        logger.error(handler_input.request_envelope)
        return respond(handler_input, 'bad_request_response', {
            'type': 'bus number' if not bus_id else 'stop number'
        })

    logger.info(f'Checking Bus {bus_id} at {stop_id}...')
    return check_bus(handler_input, bus_id, stop_id, notify_account_linking = True)

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
    bus_id, stop_id = GetBusIntent.get_bus(token, preset_id)
    logger.info(f'Bus retrieved was {bus_id} at {stop_id}')

    if not bus_id or not stop_id:
        return respond(handler_input, "no_preset_response", {
            'preset_id': preset_id
        })
    return check_bus(handler_input, bus_id, stop_id, preset_id)

def check_bus(handler_input, bus_id, stop_id, preset_id = None, notify_account_linking = False):
    minutes, stpnm = CheckBusIntent.check_bus(bus_id, stop_id)
    if stpnm:
        stpnm = stpnm.replace('&', 'and')

    logger.info('Minutes received: %s' % minutes)
    if len(minutes) == 0:
        return respond(handler_input, 'no_bus_response', {
            'bus_id': bus_id,
            'stop_id': stop_id,
            'with_preset': f'At preset {preset_id}, <break time=\\"200ms\\"/> ' if preset_id else ''
        })
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away' % minute)

    notify_account_linking = notify_account_linking and random.randint(1,5) == 5

    return respond(handler_input, "bus_time_response", {
        'bus_id': bus_id,
        'stop_id': stop_id,
        'minutes': ' <break time=\\"200ms\\"/> and '.join(minute_strings),
        'card_minutes': ' and '.join(minute_strings),
        'stop_name': stpnm,
        'with_preset': f'At preset {preset_id}, <break time=\\"200ms\\"/> ' if preset_id else '',
        'account_linking': 'For more simplicity, you can create presets to more easily get your bus times. '
            'Check the alexa app for details in the Transit Buddy skills page.' if notify_account_linking else ''
    })

sb.add_loader(FileSystemTemplateLoader(dir_path="templates", encoding='utf-8'))
sb.add_renderer(JinjaTemplateRenderer())

handler = sb.lambda_handler()