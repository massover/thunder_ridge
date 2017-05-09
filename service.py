# -*- coding: utf-8 -*-
import logging

from models import Email
import utils
import constants

from utils import logger


def handler(event, context):
    email = Email.create_from_event(event)

    logger.info('Processing email for {}'.format(email.to))
    logger.info('Event: {}'.format(event))
    if email.is_try_again:
        logger.info('\tResult: Try again')

    elif email.is_lottery_entry_recieved:
        logger.info('\tResult: Lottery Entry Received')

    elif email.is_winner:
        logger.info('\tResult: You won')
        email_address = utils.get_email_address_from_ses_email(email.to)
        email.forward(to=email_address, cc=constants.ADMIN_EMAIL_ADDRESS)

    elif email.is_confirmation:
        logger.info('\tResult: Confirm email address')
        email.make_confirmation_request()

    else:
        logger.error('\tResult: Invalid subject line {}'.format(email.subject))
        raise RuntimeError('Invalid subject line')
