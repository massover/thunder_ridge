import logging

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

import constants

from bs4 import BeautifulSoup


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def parse_confirmation_link(html):
    logging.info('Parsing html for confirmation link: {}'.format(html))

    soup = BeautifulSoup(html, 'html.parser')
    for anchor in soup.find_all('a'):
        if '?action=validate' in anchor.get('href'):
            return anchor.get('href')

    message = 'Error parsing confirmation link from confirmation email'
    logger.error(message)
    raise RuntimeError(message)


def get_email_address_from_ses_email(ses_email):
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