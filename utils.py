import re

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import constants


def parse_confirmation_link(body):
    match = re.match('.*<(.*)>\*You.*', body, re.DOTALL)
    confirmation_link = match.group(1)
    return confirmation_link.replace('\n', '')


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