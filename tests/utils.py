import random
import string
from typing import Any, Dict, Iterable, List, Optional, NamedTuple, Tuple


def get_random_session_id(length: Optional[int] = 36) -> str:
    """Returns a randomly generated session id of given length (default 36)"""
    return "".join(
        random.choice(string.ascii_letters + string.digits) for i in range(36)
    )


class Option(NamedTuple):
    key: str
    title: str
    synonyms: Optional[List[str]] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_alt: Optional[str] = None


class GoogleOptionsList(Dict):
    def __init__(self, options_list: List[Dict[str, Any]]):
        self.__dict__ = self  # Accessible as a dict

        for each_dict in options_list:
            # Iterate over each option
            key = each_dict["optionInfo"]["key"]
            title = each_dict["title"]
            description = each_dict.get("description")
            synonyms = each_dict["optionInfo"].get("synonyms")

            # Try to get image attributes if they exist
            image = each_dict.get("image")
            if image:
                image_url = image.get("url")
                image_alt = image.get("accessibilityText")
            else:
                image_url = image_alt = None

            option = Option(
                key=key,
                title=title,
                description=description,
                synonyms=synonyms,
                image_url=image_url,
                image_alt=image_alt,
            )
            setattr(self, key, option)


class WebhookRequest:
    def __init__(self, req: Dict[str, Any]):
        self.__dict__ = req

        self.session_id: str = req["session"].split("/")[-1]
        self.action: str = req["queryResult"].get("action")  # Can be None
        self.intent: str = req["queryResult"]["intent"]["displayName"]
        self.querytext: str = req["queryResult"]["queryText"]
        self.params: Dict[str, Any] = req["queryResult"]["parameters"]
        self.all_required_params_present: bool = req["queryResult"][
            "allRequiredParamsPresent"
        ]
        self.output_contexts: List[Dict[str, Any]] = req["queryResult"][
            "outputContexts"
        ]


# For general webhook request
def get_dummy_webhook_request(
    session_id: Optional[str] = None,
    action: Optional[str] = None,
    intent: Optional[str] = "",
    queryText: Optional[str] = "",
    parameters: Optional[Dict[str, Any]] = {},
    allRequiredParamsPresent: Optional[bool] = True,
) -> Dict[str, Any]:
    """Generates a dummy webhook request in json similar to dialogflow

    Taken from Dialogflow's samples:
    https://github.com/dialogflow/fulfillment-webhook-json/
    (located at requests/v2/request.json in the repo)
    """

    # Get the template
    request = {
        "responseId": "ea3d77e8-ae27-41a4-9e1d-174bd461b68c",
        "session": "projects/your-agents-project-id/agent/sessions/"
        "88d13aa8-2999-4f71-b233-39cbf3a824a0",
        "queryResult": {
            "queryText": "user's original query to your agent",
            "parameters": {"param": "param value"},
            "allRequiredParamsPresent": True,
            "fulfillmentText": "Text defined in Dialogflow's console for the "
            "intent that was matched",
            "fulfillmentMessages": [
                {
                    "text": {
                        "text": [
                            "Text defined in Dialogflow's console for the "
                            "intent that was matched"
                        ]
                    }
                }
            ],
            "outputContexts": [
                {
                    "name": "projects/your-agents-project-id/agent/sessions/"
                    "88d13aa8-2999-4f71-b233-39cbf3a824a0/contexts/generic",
                    "lifespanCount": 5,
                    "parameters": {"param": "param value"},
                }
            ],
            "intent": {
                "name": "projects/your-agents-project-id/agent/intents/"
                "29bcd7f8-f717-4261-a8fd-2d3e451b8af8",
                "displayName": "Matched Intent Name",
            },
            "intentDetectionConfidence": 1,
            "diagnosticInfo": {},
            "languageCode": "en",
        },
        "originalDetectIntentRequest": {},
    }

    # Edit session_id in request if provided
    if session_id is not None:
        parts = request["session"].split("/")
        parts[-1] = session_id
        request["session"] = "/".join(parts)

    if action is not None:
        request["queryResult"]["action"] = action

    request["queryResult"]["queryText"] = queryText
    request["queryResult"]["parameters"] = parameters
    request["queryResult"][
        "allRequiredParamsPresent"
    ] = allRequiredParamsPresent
    request["queryResult"]["intent"]["displayName"] = intent

    return request


def get_dummy_webhook_request_for_google(
    session_id: Optional[str] = None,
    action: Optional[str] = None,
    intent: Optional[str] = "",
    queryText: Optional[str] = "",
    parameters: Optional[Dict[str, Any]] = {},
    allRequiredParamsPresent: Optional[bool] = True,
    option: Optional[Tuple[str]] = None,
) -> Dict[str, Any]:
    """Generates a dummy webhook request in json similar to dialogflow when
    source is Google

    Note that option argument should be a (option_key, option_title) Tuple for
    the chosen option from a list.

    In addition to above method, some part taken from Dialogflow's samples:
    https://github.com/dialogflow/fulfillment-webhook-json/
    (located at requests/v2/ActionsOnGoogle/request.json in the repo)
    """

    original_google_request = {
        "source": "google",
        "version": "2",
        "payload": {
            "isInSandbox": True,
            "surface": {
                "capabilities": [
                    {"name": "actions.capability.SCREEN_OUTPUT"},
                    {"name": "actions.capability.AUDIO_OUTPUT"},
                    {"name": "actions.capability.WEB_BROWSER"},
                    {"name": "actions.capability.MEDIA_RESPONSE_AUDIO"},
                ]
            },
            "inputs": [
                {
                    "rawInputs": [
                        {
                            "query": "query from the user",
                            "inputType": "KEYBOARD",
                        }
                    ],
                    "arguments": [
                        {
                            "rawText": "query from the user",
                            "textValue": "query from the user",
                            "name": "text",
                        }
                    ],
                    "intent": "actions.intent.TEXT",
                }
            ],
            "user": {
                "lastSeen": "2017-10-06T01:06:56Z",
                "locale": "en-US",
                "userId": "AI_yXq-AtrRh3mJX5D-G0MsVhqun",
            },
            "conversation": {
                "conversationId": "1522951193000",
                "type": "ACTIVE",
                "conversationToken": "[]",
            },
            "availableSurfaces": [
                {
                    "capabilities": [
                        {"name": "actions.capability.SCREEN_OUTPUT"},
                        {"name": "actions.capability.AUDIO_OUTPUT"},
                    ]
                }
            ],
        },
    }

    # Google uses its conversation id as the request's session id
    if session_id is not None:
        original_google_request["payload"]["conversation"][
            "conversationId"
        ] = session_id
    else:
        # To overwrite session_id in request template
        session_id = original_google_request["payload"]["conversation"][
            "conversationId"
        ]

    if option is not None:
        # Option is a Tuple[str] of the form (OPTION_KEY, OPTION_TITLE)
        key, title = option

        # Create an input dict to append to inputs
        option_input = {
            "intent": "actions.intent.OPTION",
            "rawInputs": [{"inputType": "TOUCH", "query": title}],
            "arguments": [
                {"name": "OPTION", "textValue": key},
                {"name": "text", "rawText": title, "textValue": title,},
            ],
        }

        original_google_request["payload"]["inputs"].append(option_input)

    # Get a template
    request = get_dummy_webhook_request(
        session_id,
        action,
        intent,
        queryText,
        parameters,
        allRequiredParamsPresent,
    )

    request["originalDetectIntentRequest"] = original_google_request

    return request
