import os

DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = [os.getenv('ALLOWED_HOST')]
BRAND_NAME = os.getenv('BRAND_NAME', 'Your company name')
