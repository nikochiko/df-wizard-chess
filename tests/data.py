sample_request = {
    "responseId": "68efa569-4ba1-4b7f-9b1b-ac2865deb539",
    "queryResult": {
        "queryText": "query from the user",
        "action": "action.name.of.matched.dialogflow.intent",
        "parameters": {"a": "alice", "b": "bob", "c": "charlie"},
        "allRequiredParamsPresent": True,
        "outputContexts": [
            {
                "name": "projects/PROJECTID/agent/sessions/SESSIONID/contexts/actions_capability_screen_output"
            },
            {
                "name": "projects/PROJECTID/agent/sessions/SESSIONID/contexts/actions_capability_audio_output"
            },
            {
                "name": "projects/PROJECTID/agent/sessions/SESSIONID/contexts/google_assistant_input_type_keyboard"
            },
            {
                "name": "projects/PROJECTID/agent/sessions/SESSIONID/contexts/actions_capability_media_response_audio"
            },
            {
                "name": "projects/PROJECTID/agent/sessions/SESSIONID/contexts/actions_capability_web_browser"
            },
        ],
        "intent": {
            "name": "projects/PROJECTID/agent/intents/1f4e5bd9-a670-4161-a22e-2c97b077f29f",
            "displayName": "Name of Dialogflow Intent",
        },
        "intentDetectionConfidence": 1,
        "diagnosticInfo": {},
        "languageCode": "en-us",
    },
    "originalDetectIntentRequest": {
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
                        {"query": "query from the user", "inputType": "KEYBOARD"}
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
    },
    "session": "projects/PROJECTID/agent/sessions/SESSIONID",
}


sample_request_sessionid = "SESSIONID"
sample_request_params = {"a": "alice", "b": "bob", "c": "charlie"}


sample_options = [
    {
        "optionInfo": {"key": "first title key"},
        "description": "first description",
        "image": {
            "url": "/assistant/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
            "accessibilityText": "first alt",
        },
        "title": "first title",
    },
    {
        "optionInfo": {"key": "second"},
        "description": "second description",
        "image": {
            "url": "https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw",
            "accessibilityText": "second alt",
        },
        "title": "second title",
    },
]

sample_textToSpeech = "Options Title"
sample_response_for_google_assistant = {
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {
                "items": [{"simpleResponse": {"textToSpeech": "Options Title"}}]
            },
            "systemIntent": {
                "intent": "actions.intent.OPTION",
                "data": {
                    "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                    "listSelect": {
                        "items": [
                            {
                                "optionInfo": {"key": "first title key"},
                                "description": "first description",
                                "image": {
                                    "url": "/assistant/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
                                    "accessibilityText": "first alt",
                                },
                                "title": "first title",
                            },
                            {
                                "optionInfo": {"key": "second"},
                                "description": "second description",
                                "image": {
                                    "url": "https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw",
                                    "accessibilityText": "second alt",
                                },
                                "title": "second title",
                            },
                        ],
                    },
                },
            },
        }
    }
}

sample_google_response_template = {
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {"items": [{"simpleResponse": {"textToSpeech": ""}}]},
        }
    }
}
sample_google_response_template_with_options = {
    "payload": {
        "google": {
            "expectUserResponse": True,
            "richResponse": {"items": [{"simpleResponse": {"textToSpeech": ""}}]},
            "systemIntent": {
                "intent": "actions.intent.OPTION",
                "data": {
                    "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                    "listSelect": {"items": []},
                },
            },
        }
    }
}
