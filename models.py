import logging
import email

import requests
import boto3

import utils
import constants

logger = logging.getLogger(__name__)
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

    @property
    def body(self):
        s3 = boto3.resource('s3')
        object = s3.Object(constants.S3_BUCKET_NAME, self.message_id)
        return object.get()["Body"].read()

    @property
    def message(self):
        return email.message_from_string(self.body)

    @property
    def html(self):
        """
        When testing and sending an email to SES via gmail, the content type
        is `multipart/alternative`. When SES receives the emails from the
        server directly, the content type is `text/html`"
        """
        for part in self.message.walk():
            if part.get_content_type() == 'text/html':
                return part.get_payload()

        raise RuntimeError('Email does not contain text/html content type')

    def make_confirmation_request(self):
        confirmation_link = utils.parse_confirmation_link(self.html)
        response = requests.get(confirmation_link)
        message = ('response.url: %s\n'
                   'response.status_code: %s\n'
                   'response.text: %s')
        logger.info(message, response.url, response.status_code, response.text)

    def forward(self, destinations):
        ses = boto3.client('ses')
        self.message['From'] = constants.FROM_EMAIL_ADDRESS
        ses.send_raw_email(
            RawMessage={'Data': self.message.as_string()},
            Source=constants.FROM_EMAIL_ADDRESS,
            Destinations=destinations,
        )
        logger.info('Winning email successfully forwarded to {}'.format(' '.join(destinations)))
