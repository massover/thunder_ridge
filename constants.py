import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

API_URL = os.environ['API_URL']
TOKEN_URL = API_URL + 'o/token/'

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

SES_DETAIL_URL = API_URL + 'api/ses/'
