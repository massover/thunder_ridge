# -*- coding: utf-8 -*-
import logging

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

from models import Email
import constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    email = Email.create_from_event(event)

    logger.info('Processing email for {}'.format(email.to))
    logger.info('Event: {}'.format(event))
    if email.is_try_again:
        logger.info('\tResult: Try again')

    elif email.is_winner:
        logger.info('\tResult: You won')

    elif email.is_confirmation:
        logger.info('\tResult: Confirm email address')
        email.make_confirmation_request()

    else:
        logger.error('\tResult: Invalid subject line {}'.format(email.subject))
        raise RuntimeError('Invalid subject line')


def get_email_from_ses_email(ses_email):
    client = BackendApplicationClient(client_id=constants.CLIENT_ID)
    oauth2_session = OAuth2Session(client=client)
    oauth2_token = oauth2_session.fetch_token(
        token_url=constants.TOKEN_URL,
        client_id=constants.CLIENT_ID,
        client_secret=constants.CLIENT_SECRET,
    )
    url = constants.SES_DETAIL_URL + ses_email
    response = oauth2_session.get(url)
    response.raise_for_status()
    return response.json()['user']['email']
