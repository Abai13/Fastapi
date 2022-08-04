import os

from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_FROM = os.getenv('EMAIL_FROM')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST = os.getenv('EMAIL_HOST')
SECRET_KEY = os.getenv('SECRET_KEY')
REFRESH_SECRET_KEY = os.getenv('REFRESH_SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')
ACCESS_TOKEN_LIFETIME = os.getenv('ACCESS_TOKEN_LIFETIME')
REFRESH_TOKEN_LIFETIME = os.getenv('REFRESH_TOKEN_LIFETIME')