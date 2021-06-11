import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_intent_name, is_request_type
from ask_sdk_core.view_resolvers import FileSystemTemplateLoader
from ask_sdk_jinja_renderer import JinjaTemplateRenderer

from agencies.chicago_cta_bus import ChicagoCTABus
from agencies.chicago_cta_train import ChicagoCTATrain
from agencies.chicago_pace_bus import ChicagoPaceBus
from agencies.umich_magic_bus import UMichMagicBus

from helpers import utils

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
    handler_input.response_builder.speak("Ok!")
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

@sb.request_handler(can_handle_func=is_intent_name("GetBusIntent"))
def get_bus_handler(handler_input):
    preset_id = get_slot_value(handler_input, 'preset_id', '1')
    logger.info(f'Getting Route at preset {preset_id}...')

    user = handler_input.request_envelope.context.system.user
    token = user.access_token;

    preset = utils.get_bus(token, preset_id)
    logger.info(f'Route retrieved was {preset.route_id} at {preset.stop_id}')

    if not preset:
        return respond(handler_input, "no_preset_response", {
            'preset_id': preset_id
        })

    minutes, route_response_text, = __get_agency(preset.agency_name).check_bus(preset)
    route_response_text = route_response_text.replace('&', 'and')

    logger.info('Minutes received: %s' % minutes)
    if len(minutes) == 0:
        return respond(handler_input, 'no_bus_response', {
            'route_response_text': route_response_text,
            'preset_id': preset.preset_id
        })
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away' % minute)

    return respond(handler_input, "bus_time_response", {
        'route_response_text': route_response_text,
        'minutes': ' <break time=\\"200ms\\"/> and '.join(minute_strings),
        'card_minutes': ' and '.join(minute_strings),
        'preset_id': preset.preset_id
    })

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

def __get_agency(agency):
    if agency == 'Chicago CTA Bus':
        return ChicagoCTABus()
    elif agency == 'Chicago CTA Train':
        return ChicagoCTATrain()
    elif agency == 'Chicago Pace Bus':
        return ChicagoPaceBus()
    elif agency == 'UMich Magic Bus':
        return UMichMagicBus()
    else:
        return ChicagoCTABus()

sb.add_loader(FileSystemTemplateLoader(dir_path="templates", encoding='utf-8'))
sb.add_renderer(JinjaTemplateRenderer())

handler = sb.lambda_handler()
