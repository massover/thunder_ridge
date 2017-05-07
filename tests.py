import requests
from mock import patch, PropertyMock

import pytest

from models import Email
from utils import parse_confirmation_link, get_email_address_from_ses_email


CONFIRMATION_LINK = 'https://lottery.broadwaydirect.com?action=validate&u=13723977&t=5e4bc398448a91fb398e3320d877f24d'
CONFIRMATION_LINK_HTML = '<a href="{}">'.format(CONFIRMATION_LINK)


def test_parse_confirmation_link():
    html = ('<a href="href-1">' +
            CONFIRMATION_LINK_HTML +
            '<a href="href-2">')

    link = parse_confirmation_link(html)
    assert link == CONFIRMATION_LINK


def test_parse_confirmation_link_raises_runtime_error_when_it_fails_parse():
    html = ('<a href="href-1">'
            '<a href="href-2">')

    with pytest.raises(RuntimeError):
        link = parse_confirmation_link(html)


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

    email = get_email_address_from_ses_email('this-is-mocked@example.com')
    assert email == 'user@example.com'


@patch('requests.get')
@patch.object(Email, 'html',  new_callable=PropertyMock, return_value=CONFIRMATION_LINK_HTML)
def test_make_confirmation_request(mock_html, mock_get):
    email = Email('message_id', 'to', Email.CONFIRMATION_SUBJECT_TEXT)
    email.make_confirmation_request()


@patch('boto3.client')
@patch.object(Email, 'html', new_callable=PropertyMock, return_value=CONFIRMATION_LINK_HTML)
@patch.object(Email, 'body', new_callable=PropertyMock, return_value=CONFIRMATION_LINK_HTML)
def test_forward(mock_body, mock_html, mock_get):
    email = Email('message_id', 'to', Email.CONFIRMATION_SUBJECT_TEXT)
    to = 'to@example.com'
    cc = 'cc@example.com'
    email.forward(to, cc)





