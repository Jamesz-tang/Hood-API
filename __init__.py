import os

from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

app_name = os.getenv('FLASK_APP')



