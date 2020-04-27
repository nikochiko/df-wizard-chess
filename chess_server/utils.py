import json
from typing import Any, Dict, List, NamedTuple, Optional, Union

import chess


def get_session_by_req(req: Dict[str, Any]) -> str:
    """Get Session ID by DialogFlow request"""
    return req.get("session").split("/")[-1]


def get_params_by_req(req: Dict[str, Any]) -> Dict[str, str]:
    """Get parameters by DialogFlow request"""
    return req.get("queryResult").get("parameters")


def get_response_template_for_google_assistant(
    options: Optional[bool] = False,
) -> Dict[str, Any]:
    """Return template for response for Google Assistant"""

    template = {
        "payload": {
            "google": {
                "expectUserResponse": True,
                "richResponse": {"items": [{"simpleResponse": {"textToSpeech": ""}}],},
            }
        }
    }

    if options:
        template["payload"]["google"]["systemIntent"] = {
            "intent": "actions.intent.OPTION",
            "data": {
                "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
                "listSelect": {"items": []},
            },
        }

    return template


def generate_response_for_google_assistant(
    textToSpeech: str,
    expectUserResponse: Optional[bool] = True,
    options: Optional[List[Dict[str, Union[str, Dict[str, str]]]]] = None,
) -> Dict[str, Any]:
    """
	Generate response from given data.


	For example, 
	```python
	generate_response_for_google_assistant(textToSpeech='This is a simple response')
	```
	would return:


	```json
	{
		"payload": {
    		"google": {
      			"expectUserResponse": true,
      			"richResponse": {
        			"items": [
         				{
            				"simpleResponse": {
              					"textToSpeech": "this is a simple response"
            				}
          				}
        			]
   	  			}
			}
		}
	}
	```

	And, for a more complex example:
	```python
	options = [
		{
			'optionInfo': {'key': 'first title key'},
			'description': 'first description',
			'image': {
				'url': '/assistant/images/badges/XPM_BADGING_GoogleAssistant_VER.png',
				accessibilityText: 'first alt',
			},
			'title': 'first title',
		},
		{
			'optionInfo': {'key': 'second'},
			'description': 'second description',
			'image': {
				'url': 'https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw',
				accessibilityText: 'second alt',
			},
			'title': 'second title',
		},
	]

	generate_response_for_google_assistant(
		textToSpeech='Choose a item',
		options=options)
	```

	should give:

	```json
	{
	  "payload": {
	    "google": {
	      "expectUserResponse": true,
	      "richResponse": {
	        "items": [
	          {
	            "simpleResponse": {
	              "textToSpeech": "Choose a item"
	            }
	          }
	        ]
	      },
	      "systemIntent": {
	        "intent": "actions.intent.OPTION",
	        "data": {
	          "@type": "type.googleapis.com/google.actions.v2.OptionValueSpec",
	          "listSelect": {
	            "title": "Hello",
	            "items": [
	              {
	                "optionInfo": {
	                  "key": "first title key"
	                },
	                "description": "first description",
	                "image": {
	                  "url": "/assistant/images/badges/XPM_BADGING_GoogleAssistant_VER.png",
	                  "accessibilityText": "first alt"
	                },
	                "title": "first title"
	              },
	              {
	                "optionInfo": {
	                  "key": "second"
	                },
	                "description": "second description",
	                "image": {
	                  "url": "https://lh3.googleusercontent.com/Nu3a6F80WfixUqf_ec_vgXy_c0-0r4VLJRXjVFF_X_CIilEu8B9fT35qyTEj_PEsKw",
	                  "accessibilityText": "second alt"
	                },
	                "title": "second title"
	              }
	            ]
	          }
	        }
	      }
	    }
	  }
	}
	```

	Note: Setting the `expectUserResponse` param to False will mark the end of conversation 
	"""

    # Get template for response
    template = get_response_template_for_google_assistant(options=bool(options))

    # Modify the dict as per the arguments
    template["payload"]["google"]["expectUserResponse"] = expectUserResponse
    template["payload"]["google"]["richResponse"]["items"][0]["simpleResponse"][
        "textToSpeech"
    ] = textToSpeech

    # If options List is given
    if options:
        print(template)
        template["payload"]["google"]["systemIntent"]["data"]["listSelect"][
            "items"
        ] = options

    # Return DICT
    return template
