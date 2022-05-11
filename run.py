from cachetools import TTLCache
from datetime import timedelta
import logging
import os
import sys

import pyrebase
from firebasedata import LiveData


# The name of the Firebase app, used to construct the REST URL.
FIREBASE_APP_NAME = os.getenv('TC_FIREBASE_APP_NAME', 'theater-commander')

# Path to service account credentials file
FIREBASE_KEY_PATH = os.getenv('TC_FIREBASE_KEY_PATH', '/home/pi/.firebasekey')

# Firebase web API key
FIREBASE_API_KEY = os.getenv('TC_FIREBASE_API_KEY')

# Firebase Realtime Database URL
FIREBASE_DATABASE_URL = os.getenv('TC_FIREBASE_DATABASE_URL')

# The path to message collection in the database
FIREBASE_MESSAGE_PATH = 'message'

# FIFO path
FIFO_PATH = os.getenv('TC_FIFO_PATH', '/tmp/p-cec-fix')

# Logging
LOG_LEVEL = os.getenv('TC_LOGGING_LEVEL', 'DEBUG')

logging.basicConfig(
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    level=LOG_LEVEL,
    stream=sys.stdout
)

logger = logging.getLogger(__name__)

NAME = 'firebase'
AUTH_DOMAIN = '{}.firebaseapp.com'.format(FIREBASE_APP_NAME)
STORAGE_BUCKET = '{}.appspot.com'.format(FIREBASE_APP_NAME)
TTL = timedelta(minutes=75)
CACHE_SIZE = 2  # items
CACHE_TTL = 5  # seconds

firebase_config = {
    'apiKey': FIREBASE_API_KEY,
    'authDomain': AUTH_DOMAIN,
    'databaseURL': FIREBASE_DATABASE_URL,
    'storageBucket': STORAGE_BUCKET,
    'serviceAccount': FIREBASE_KEY_PATH,
}
firebase_app = pyrebase.initialize_app(firebase_config)
live_data = LiveData(firebase_app, FIREBASE_MESSAGE_PATH, TTL)
message_cache = TTLCache(CACHE_SIZE, CACHE_TTL)

def handle_message(sender, value=None, path=None):
    logger.debug("handle_message called with value=%s path=%s")

    if value == 'on':
        logger.info("ON command received")
        if value in message_cache:
            logger.debug("ON command received in last %s seconds. Ignoring.", CACHE_TTL)
            return

        send_on()
        message_cache[value] = 1

    elif value == 'off':
        logger.info("OFF command received")
        if value in message_cache:
            logger.debug("OFF command received in last %s seconds. Ignoring.", CACHE_TTL)
            return

        send_off()
        message_cache[value] = 1

    else:
        logger.error("Unknown value: %s", value)


    live_data.set_data('/', None)


live_data.signal('/').connect(handle_message)


def send_on():
    write_fifo('1')


def send_off():
    write_fifo('0')


def write_fifo(value):
    with open(FIFO_PATH, 'w') as fifo:
        fifo.write(value)


def listen():
    live_data.get_data()


if __name__ == '__main__':
    listen()
