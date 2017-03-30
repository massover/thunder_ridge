import quopri
import logging

import requests
import boto3

import utils

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Email(object):
    TRY_AGAIN_SUBJECT_TEXT = 'Lottery Results: Try Again'
    WINNER_SUBJECT_TEXT = 'Lottery Results - YOU WON!'
    CONFIRMATION_SUBJECT_TEXT = 'Action Required: Confirm your email address'

    def __init__(self, message_id, to, subject):
        self.message_id = message_id
        self.to = to
        self.subject = subject

    @classmethod
    def create_from_event(cls, event):
        try:
            records = event.get('Records')
            ses = records[0].get('ses')
            mail = ses.get('mail')
            message_id = mail.get('messageId')
            common_headers = mail.get('commonHeaders')
            to = common_headers.get('to')[0]
            subject = common_headers.get('subject')
        except (IndexError, KeyError):
            logger.error('Invalid event')
            raise RuntimeError('Invalid event')

        return cls(message_id, to, subject)

    @property
    def is_try_again(self):
        return self.TRY_AGAIN_SUBJECT_TEXT in self.subject

    @property
    def is_winner(self):
        return self.WINNER_SUBJECT_TEXT in self.subject

    @property
    def is_confirmation(self):
        return self.CONFIRMATION_SUBJECT_TEXT in self.subject

    def make_confirmation_request(self):
        s3 = boto3.resource('s3')
        object = s3.Object('killington', self.message_id)
        body = object.get()["Body"].read()
        confirmation_link = utils.parse_confirmation_link(quopri.decodestring(body))
        response = requests.get(confirmation_link)
        message = ('response.url: %s\n'
                   'response.status_code: %s\n'
                   'response.text: %s')
        logger.info(message, response.url, response.status_code, response.text)
