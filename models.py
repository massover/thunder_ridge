import logging
import email
from email.mime.text import MIMEText

import requests
import boto3

import utils
import settings

from utils import logger


class Email(object):
    TRY_AGAIN_SUBJECT_TEXT = 'Lottery Results: Try Again'
    WINNER_SUBJECT_TEXT = 'Lottery Results - YOU WON!'
    CONFIRMATION_SUBJECT_TEXT = 'Action Required: Confirm your email address'
    LOTTERY_ENTRY_RECEIVED_TEXT = 'Lottery Entry Received'
    LOTTERY_PAYMENT_CONFIRMATION = 'Lottery Payment Confirmation'

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
            logging.info('message_id: %s to: %s subject: %s', message_id, to, subject)
        except (IndexError, KeyError):
            logger.error('Invalid event')
            raise RuntimeError('Invalid event')

        return cls(message_id, to, subject)

    @property
    def is_lottery_payment_confirmation(self):
        return self.LOTTERY_PAYMENT_CONFIRMATION in self.subject

    @property
    def is_lottery_entry_recieved(self):
        return self.LOTTERY_ENTRY_RECEIVED_TEXT in self.subject

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
        object = s3.Object(settings.S3_BUCKET_NAME, self.message_id)
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
                return part.get_payload(decode=True)

        raise RuntimeError('Email does not contain text/html content type')

    def make_confirmation_request(self):
        confirmation_link = utils.parse_confirmation_link(self.html)
        response = requests.get(confirmation_link)
        message = ('response.url: %s\n'
                   'response.status_code: %s\n'
                   'response.text: %s')
        logger.info(message, response.url, response.status_code, response.text)

    def forward(self, to, cc):
        ses = boto3.client('ses')

        mime = MIMEText(self.html, 'html')
        mime['To'] = to
        mime['Cc'] = cc
        mime['From'] = settings.FROM_EMAIL_ADDRESS
        mime['Subject'] = self.message['Subject']

        ses.send_raw_email(
            RawMessage={'Data': mime.as_string()},
            Source=settings.FROM_EMAIL_ADDRESS,
            Destinations=[to, cc],
        )
        logger.info('{} forwarded to {} {}'.format(self.message['Subject'], to, cc))
