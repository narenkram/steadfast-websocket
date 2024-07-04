from api_helper import NorenApiPy
from dotenv import load_dotenv
import os
import logging
import time

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Flag to tell us if the websocket is open
socket_opened = False

# Event handlers
def event_handler_order_update(message):
    print("order event: " + str(message))

def event_handler_quote_update(message):
    print("quote event: {0}".format(time.strftime('%d-%m-%Y %H:%M:%S')) + str(message))

def open_callback():
    global socket_opened
    socket_opened = True
    print('app is connected')
    
    # Subscribe to the desired symbol
    api.subscribe(['NFO|55237'])

# Initialize API
api = NorenApiPy()

# Set token and user id
usersession = os.getenv('USERSESSION')
userid = os.getenv('USERID')

# Set up the session
ret = api.set_session(userid=userid, password='', usertoken=usersession)

if ret is not None:
    # Start the websocket
    ret = api.start_websocket(
        order_update_callback=event_handler_order_update,
        subscribe_callback=event_handler_quote_update,
        socket_open_callback=open_callback
    )
    print(ret)

# Keep the script running
while True:
    time.sleep(1)