import re


def parse_confirmation_link(body):
    match = re.match('.*<(.*)>\*You.*', body, re.DOTALL)
    confirmation_link = match.group(1)
    return confirmation_link.replace('\n', '')