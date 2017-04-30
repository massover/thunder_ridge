# -*- coding: utf-8 -*-
import logging

from models import Email
import utils
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
        email = utils.get_email_from_ses_email(email.to)
        destinations = [email, constants.ADMIN_EMAIL]
        email.forward(destinations)

    elif email.is_confirmation:
        logger.info('\tResult: Confirm email address')
        email.make_confirmation_request()

    else:
        logger.error('\tResult: Invalid subject line {}'.format(email.subject))
        raise RuntimeError('Invalid subject line')
