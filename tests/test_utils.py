from chess_server import utils
from . import data


def test_get_session_by_req():

    result = utils.get_session_by_req(data.sample_request)
    assert result == data.sample_request_sessionid


def test_get_params_by_req():

    result = utils.get_params_by_req(data.sample_request)
    assert result == data.sample_request_params


def test_generate_response_for_google_assistant():

    result = utils.generate_response_for_google_assistant(
        textToSpeech=data.sample_textToSpeech, options=data.sample_options
    )
    assert result == data.sample_response_for_google_assistant


def test_get_response_template_for_google_assistant():

    result = utils.get_response_template_for_google_assistant()
    assert result == data.sample_google_response_template


def test_get_response_template_for_google_assistant_with_options():

    result = utils.get_response_template_for_google_assistant(options=True)
    assert result == data.sample_google_response_template_with_options
