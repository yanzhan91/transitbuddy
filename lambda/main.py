import logging

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name

import CheckBusIntent
import SetBusIntent
import GetBusIntent

from ask_sdk_core.view_resolvers import FileSystemTemplateLoader
from ask_sdk_jinja_renderer import JinjaTemplateRenderer

sb = SkillBuilder()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@sb.request_handler(can_handle_func=is_request_type("LaunchRequest"))
def launch_request_handler(handler_input):
    return handler_input.generate_template_response("launch_response", {'test': 'test'}, file_ext='jinja')

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.HelpIntent"))
def help_request_handler(handler_input):
    return handler_input.generate_template_response("help_response", None, file_ext='jinja')

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

    speech = "Help!!"
    # speech = "Sorry, there was some problem. Please try again!!"
    handler_input.response_builder.speak(speech).ask(speech)

    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("AMAZON.FallbackIntent"))
def fallback_handler(handler_input):
    """AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """
    # type: (HandlerInput) -> Response
    speech = (
        "The Hello World skill can't help you with that.  "
        "You can say hello!!")
    reprompt = "You can say hello!!"
    handler_input.response_builder.speak(speech).ask(reprompt)
    return handler_input.response_builder.response

@sb.request_handler(can_handle_func=is_intent_name("CheckBusIntent"))
def check_bus_handler(handler_input):
    # session_attr = handler_input.attributes_manager.session_attributes
    slots = handler_input.request_envelope.request.intent.slots

    # session_attr['request'] = 'check_bus'
    bus_id = slots['bus_id'].value
    stop_id = slots['stop_id'].value

    logger.info(f'Checking Bus {bus_id} at {stop_id}...')
    return check_bus(handler_input, bus_id, stop_id)

@sb.request_handler(can_handle_func=is_intent_name("GetBusIntent"))
def get_bus_handle(handler_input):
    slots = handler_input.request_envelope.request.intent.slots
    preset_id = slots['preset_id'].value if 'preset_id' in slots and slots['preset_id'].value else 1
    user_id = handler_input.request_envelope.context.system.user.user_id

    logger.info(f'Getting Bus at preset {preset_id}...')
    return get_bus(handler_input, user_id, preset_id)

@sb.request_handler(can_handle_func=is_intent_name("SetBusIntent"))
def set_bus_handle(handler_input):
    slots = handler_input.request_envelope.request.intent.slots
    bus_id = slots['bus_id'].value
    stop_id = slots['stop_id'].value
    preset_id = slots['preset_id'].value if 'preset_id' in slots else 1
    user_id = handler_input.request_envelope.context.system.user.user_id

    logger.info(f'Setting Bus {bus_id} at {stop_id} for preset {preset_id}...')
    return set_bus(handler_input, user_id, bus_id, stop_id, preset_id)

def respond(handler_input, response_file, data_map):
    return handler_input.generate_template_response(response_file, data_map, file_ext='jinja')

def set_bus(handler_input, user_id, bus_id, stop_id, preset_id):
    logger.info(f'Setting Bus {bus_id} at {stop_id} for preset {preset_id}...')
    SetBusIntent.set_bus(user_id, bus_id, stop_id, preset_id)
    logger.info(f'Set bus {bus_id} at {stop_id} for {preset_id} was successful')
    return respond(handler_input, 'set_bus_response', {
        'bus_id': bus_id,
        'stop_id': stop_id,
        'preset_id': preset_id
    })

def get_bus(handler_input, user_id, preset_id):
    logger.info('Getting Bus at preset %s...' % preset_id)
    bus_id, stop_id = GetBusIntent.get_bus(user_id, preset_id)
    logger.info('Bus retrieved was %s at %s' % (bus_id, stop_id))

    if not bus_id or not stop_id:
        return respond(handler_input, "no_preset_response", {
            'preset_id': preset_id
        })
    return check_bus(handler_input, bus_id, stop_id)

def check_bus(handler_input, bus_id, stop_id):
    minutes, stpnm = CheckBusIntent.check_bus(bus_id, stop_id)
    if stpnm:
        stpnm = stpnm.replace('&', 'and')

    logging.info('Minutes received: %s' % minutes)
    if len(minutes) == 0:
        return respond(handler_input, 'no_bus_response', {
            'bus_id': bus_id,
            'stop_id': stop_id    
        })
    minute_strings = []
    for minute in minutes:
        minute_strings.append('%s minutes away <break time="200ms"/>' % minute)
    minute_string = ' and '.join(minute_strings)

    return respond(handler_input, "bus_time_response", {
        'bus_id': bus_id,
        'stop_id': stop_id,
        'minutes': minute_string,
        'stop_name': stpnm
    })

sb.add_loader(FileSystemTemplateLoader(dir_path="templates", encoding='utf-8'))
sb.add_renderer(JinjaTemplateRenderer())

handler = sb.lambda_handler()