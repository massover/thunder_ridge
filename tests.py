import quopri

import requests
from mock import patch

from models import Email
from utils import parse_confirmation_link
from service import get_email_from_ses_email


def test_get_confirmation_link():
    with open('confirmation.txt') as fp:
        body = fp.read()

    link = parse_confirmation_link(quopri.decodestring(body))
    assert link == "https://lottery.broadwaydirect.com/?action=validate&u=12402178&t=6ed51ecc573ea1982a3124e41fc4ac6f"


def test_email_create_from_event():
    event = {
        'Records': [{
            'ses': {
                'mail': {
                    'commonHeaders': {
                        'to': ['user@example.com'],
                        'subject': 'hello world!',
                    },
                    'messageId': '1'
                }
            }
        }]
    }
    email = Email.create_from_event(event)
    assert email.to == 'user@example.com'
    assert email.subject == 'hello world!'
    assert email.message_id == '1'


def test_email_is_confirmation():
    email = Email('message_id', 'to', Email.CONFIRMATION_SUBJECT_TEXT)
    assert email.is_confirmation


def test_email_is_winner():
    email = Email('message_id', 'to', Email.WINNER_SUBJECT_TEXT)
    assert email.is_winner


def test_email_is_try_again():
    email = Email('message_id', 'to', Email.TRY_AGAIN_SUBJECT_TEXT)
    assert email.is_try_again


@patch('requests_oauthlib.OAuth2Session.fetch_token')
@patch('requests_oauthlib.OAuth2Session.get')
def test_get_email_from_ses_email(mock_get, _):
    response = requests.Response()
    response.json = lambda: {'user': {'email': 'user@example.com'}}
    mock_get.return_value = response

    email = get_email_from_ses_email('this-is-mocked@example.com')
    assert email == 'user@example.com'

