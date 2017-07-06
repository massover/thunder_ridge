# -*- coding: utf-8 -*-
from models import Email
import utils
import settings

from utils import logger


def handler(event, context):
    logger.info('Event: {}'.format(event))
    email = Email.create_from_event(event)
    if email.is_try_again:
        logger.info('Result: Try again')

    elif email.is_lottery_entry_recieved:
        logger.info('Result: Lottery Entry Received')

    elif email.is_winner:
        logger.info('Result: You won')
        email_address = utils.get_email_address_from_ses_email(email.to)
        email.forward(to=email_address, cc=settings.ADMIN_EMAIL_ADDRESS)

    elif email.is_confirmation:
        logger.info('Result: Confirm email address')
        email.make_confirmation_request()

    elif email.is_lottery_payment_confirmation:
        logger.info('Result: Lottery payment confirmation')
        email_address = utils.get_email_address_from_ses_email(email.to)
        email.forward(to=email_address, cc=settings.ADMIN_EMAIL_ADDRESS)

    else:
        logger.error('Result: Invalid subject line {}'.format(email.subject))
