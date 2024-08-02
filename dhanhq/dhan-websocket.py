import asyncio
import websockets
import json
import logging
import requests
from marketfeed import DhanFeed, Ticker

logging.basicConfig(level=logging.DEBUG)

# Queue to hold messages from Dhan feed
message_queue = asyncio.Queue()

# Function to fetch credentials and subscription details from the server
def fetch_credentials():
    try:
        response = requests.get('http://localhost:3000/dhan-websocket-data')
        response.raise_for_status()
        data = response.json()
        return data['clientId'], data['accessToken'], data['exchangeSegment'], data['securityId']
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve data: {e}")
        return None, None, None, None

async def wait_for_data():
    while True:
        client_id, access_token, exchange_segment, security_id = await asyncio.get_event_loop().run_in_executor(None, fetch_credentials)
        if client_id and access_token and exchange_segment is not None and security_id is not None:
            return client_id, access_token, exchange_segment, security_id
        await asyncio.sleep(5)  # Wait for 5 seconds before trying again

# Type of data subscription
subscription_code = Ticker

async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)
    await message_queue.put(message)  # Put the message into the queue

print("Subscription code :", subscription_code)

async def setup_api_connection(client_id, access_token, exchange_segment, security_id):
    instruments = [(str(exchange_segment), str(security_id))]  # Ensure these are strings

    feed = DhanFeed(client_id,
        access_token,
        instruments,
        subscription_code,
        on_connect=on_connect,
        on_message=on_message)

    # Ensure the DhanFeed connection is awaited
    await feed.connect()

async def websocket_server(websocket, path):
    try:
        while True:
            message = await message_queue.get()  # Get message from the queue
            await websocket.send(json.dumps(message))  # Send message to the client
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

async def start_websocket_server():
    server = await websockets.serve(websocket_server, "localhost", 8767)
    logging.info("WebSocket server started.")
    await server.wait_closed()

async def main():
    global loop
    loop = asyncio.get_running_loop()

    try:
        # Start WebSocket server
        websocket_server_task = asyncio.create_task(start_websocket_server())

        # Wait for valid credentials and subscription details from the server
        logging.info("Waiting for valid data...")
        client_id, access_token, exchange_segment, security_id = await wait_for_data()
        logging.info(f"Using client_id: {client_id[:5]}..., access_token: {access_token[:5]}..., exchange_segment: {exchange_segment}, security_id: {security_id}")

        # Set up API connection
        await setup_api_connection(client_id, access_token, exchange_segment, security_id)

        # Wait for the WebSocket server to finish
        await websocket_server_task
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())