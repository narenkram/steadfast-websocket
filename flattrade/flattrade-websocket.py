import asyncio
import websockets
import json
import logging
from api_helper import NorenApiPy
import requests
import time

logging.basicConfig(level=logging.DEBUG)

# Flag to tell us if the websocket is open
socket_opened = False

# Initialize the API object
api = NorenApiPy()

# Event handlers
def event_handler_order_update(message):
    print("order event: " + str(message))

def event_handler_quote_update(message):
    print("quote event: {0}".format(time.strftime('%d-%m-%Y %H:%M:%S')) + str(message))
    asyncio.run_coroutine_threadsafe(quote_queue.put(message), loop)

async def get_credentials_and_security_ids():
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get('http://localhost:3000/flattrade-websocket-data')
        )
        response.raise_for_status()
        data = response.json()
        usersession = data.get('usersession', '')
        userid = data.get('userid', '')
        defaultCallSecurityId = data.get('defaultCallSecurityId', '')
        defaultPutSecurityId = data.get('defaultPutSecurityId', '')
        
        if usersession and userid and defaultCallSecurityId and defaultPutSecurityId:
            logging.info("Valid data retrieved successfully")
            return usersession, userid, defaultCallSecurityId, defaultPutSecurityId
        else:
            logging.info("Waiting for valid data...")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve data: {e}")
        return None, None, None, None

async def wait_for_data():
    while True:
        usersession, userid, defaultCallSecurityId, defaultPutSecurityId = await get_credentials_and_security_ids()
        if usersession and userid and defaultCallSecurityId and defaultPutSecurityId:
            return usersession, userid, defaultCallSecurityId, defaultPutSecurityId
        await asyncio.sleep(5)  # Wait for 5 seconds before trying again

async def setup_api_connection(usersession, userid, defaultCallSecurityId, defaultPutSecurityId):
    global api
    # Set up the session
    ret = api.set_session(userid=userid, password='', usertoken=usersession)

    if ret is not None:
        # Start the websocket
        ret = api.start_websocket(
            order_update_callback=event_handler_order_update,
            subscribe_callback=event_handler_quote_update,
            socket_open_callback=lambda: open_callback(defaultCallSecurityId, defaultPutSecurityId)
        )
        print(ret)
    else:
        raise Exception("Failed to set up API session")

def open_callback(defaultCallSecurityId, defaultPutSecurityId):
    global socket_opened
    socket_opened = True
    print('app is connected')
    
    # Subscribe to the desired symbols
    api.subscribe(['NSE|26000', f'NFO|{defaultCallSecurityId}', f'NFO|{defaultPutSecurityId}'])

quote_queue = asyncio.Queue()

async def websocket_server(websocket, path):
    while True:
        try:
            # Wait for quote updates
            quote = await quote_queue.get()
            await websocket.send(json.dumps(quote))
        except websockets.exceptions.ConnectionClosed:
            break

async def main():
    global loop
    loop = asyncio.get_running_loop()

    try:
        # Wait for valid credentials and security IDs
        logging.info("Waiting for valid data...")
        usersession, userid, defaultCallSecurityId, defaultPutSecurityId = await wait_for_data()
        logging.info(f"Using usersession: {usersession[:5]}..., userid: {userid}, defaultCallSecurityId: {defaultCallSecurityId}, defaultPutSecurityId: {defaultPutSecurityId}")

        # Set up API connection
        await setup_api_connection(usersession, userid, defaultCallSecurityId, defaultPutSecurityId)

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8765)
        await server.wait_closed()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
