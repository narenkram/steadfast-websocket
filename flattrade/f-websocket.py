from api_helper import NorenApiPy
import requests
import os
import logging
import time

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

def get_credentials():
    try:
        response = requests.get('http://localhost:3000/flattrade-websocket-credentials')
        response.raise_for_status()  # Raises an HTTPError for bad responses
        credentials = response.json()
        logging.info("Credentials retrieved successfully")
        return credentials['usersession'], credentials['userid']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve credentials: {e}")
        raise Exception("Failed to retrieve credentials from server")

try:
    # Get token and user id
    usersession, userid = get_credentials()
    logging.info(f"Using usersession: {usersession[:5]}... and userid: {userid}")

    # ... rest of your Python code ...

except Exception as e:
    logging.error(f"An error occurred: {e}")

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