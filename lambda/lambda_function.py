# -*- coding: utf-8 -*-
import time

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils
import urllib.parse
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

import http.client
import json
def send_get_request(params):
    #nos hace falta el token
    conn = http.client.HTTPConnection("smarttechnologiesurv.000webhostapp.com")
    url = "/api/authorization.php"
    json_data = {
        "publicKey": "TOKENDEPROVA"
    }
    headers = {
        "Content-Type": "application/json"
    }
    conn.request("POST",url,body=json.dumps(json_data),headers=headers)
    response = conn.getresponse()
    response = response.read().decode()
    print(response)
    json_data = json.loads(response)
    token = json_data["token"]
    url = "/api/testData.php?" + params+"&float=1" #indicamos que no hace falta dividirlos
    print(url)
    headers = {
        "Authorization": token
    }
    conn.request("GET", url,headers=headers)
    response = conn.getresponse()

    data = response.read().decode()
    print(data)
    conn.close()
    return data

# Handler para la apertura de la skill
class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "¡Hola! Bienvenido."
        handler_input.response_builder.speak(speak_output)
        return handler_input.response_builder.response
class StartBalanceHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("StartBalance")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        current_position = session_attr.get("current_position", 0)
        session_attr["current_position"] = 0 #iniciem a 0
        speak_output = "Empieza el test de equilibrio. Pon un pie al lado del otro durante 10 segundos, cuando acabes di Fin ejercicio"  
        current_timestamp = str(time.time())
        send_get_request("testType=2&start="+current_timestamp)
        handler_input.response_builder.speak(speak_output)
        
        return handler_input.response_builder.response

class ChairStartHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("testCadira")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        current_position = session_attr.get("chair", 1)
        session_attr["chair"] = 1 #iniciem a 1
        speak_output = "Empieza el test de levantar-se de la silla. Levántate y di 'Levantado' cuando te hayas levantado por completo"  
        current_timestamp = str(time.time())
        send_get_request("testType=1&start="+current_timestamp)
        handler_input.response_builder.speak(speak_output)
        
        return handler_input.response_builder.response
class ChairChangeHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("fiCadira")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        current_position = session_attr.get("chair", 1)
        if(current_position == 1):
            session_attr["chair"] = 0 # posem a 0
            speak_output = "¡Genial! Test finalizado"  
            current_timestamp = str(time.time())
            send_get_request("testType=1&end="+current_timestamp)
        handler_input.response_builder.speak(speak_output)
        
        return handler_input.response_builder.response
# Manejador para el cambio de posición
class ChangePositionHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("continueTest")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        current_position = session_attr.get("current_position", -1)
        positions = [
            
            "¡Genial!. Ahora pon los pies en diagonal",
            "Para acabar, pon un pie delante del otro"
        ]
        if current_position == -1:
            speak_output = "Para eso debes iniciar un test primero"
         
        elif current_position < len(positions):
            speak_output = positions[current_position]+" durante 10 segundos, cuando acabes di Fin ejercicio"
            session_attr["current_position"] = current_position + 1
            
        else:
            session_attr["current_position"] = -1
            speak_output = "¡Enhorabuena! Has finalizado el ejercicio"
            current_timestamp = str(time.time())
            send_get_request("testType=2&end="+current_timestamp)
        
        handler_input.response_builder.speak(speak_output)
        
        return handler_input.response_builder.response



class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "You can say hello to me! How can I help?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")
        speech = "Hmm, I'm not sure. You can say Hello or Help. What would you like to do?"
        reprompt = "I didn't catch that. What can I help you with?"

        return handler_input.response_builder.speak(speech).ask(reprompt).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(StartBalanceHandler())
sb.add_request_handler(ChairStartHandler())
sb.add_request_handler(ChairChangeHandler())
sb.add_request_handler(ChangePositionHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers


lambda_handler = sb.lambda_handler()