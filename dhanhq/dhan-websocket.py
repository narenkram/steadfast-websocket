import asyncio
import websockets
import json
import logging
from dhanhq import marketfeed
import requests

logging.basicConfig(level=logging.DEBUG)

# Flag to tell us if the websocket is open
socket_opened = False

# Remove hardcoded Dhan Client ID and Access Token
client_id = ""
access_token = ""

# Structure for subscribing is ("exchange_segment","security_id")
instruments = [(1, "1333"), (0, "13")]

# Type of data subscription
subscription_code = marketfeed.Ticker

# Event handlers
async def on_connect(instance):
    global socket_opened
    socket_opened = True
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)
    logging.info(f"Quote update received: {message}")
    await quote_queue.put(message)

quote_queue = asyncio.Queue()

async def get_credentials_and_security_ids():
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get("http://localhost:3000/dhan-websocket-data")
        )
        response.raise_for_status()
        data = response.json()
        accessToken = data.get("accessToken", "")
        clientId = data.get("clientId", "")
        instruments = data.get("instruments", "")
        subscription_code = data.get("subscription_code", "")

        if accessToken and clientId and instruments and subscription_code:
            logging.info("Valid data retrieved successfully")
            return accessToken, clientId, instruments, subscription_code
        else:
            logging.info("Waiting for valid data...")
            return None, None, None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve data: {e}")
        return None, None, None, None

async def wait_for_data():
    while True:
        accessToken, clientId, instruments, subscription_code = (
            await get_credentials_and_security_ids()
        )
        if accessToken and clientId and instruments and subscription_code:
            return accessToken, clientId, instruments, subscription_code
        await asyncio.sleep(5)  # Wait for 5 seconds before trying again

async def websocket_server(websocket, path):
    try:
        # Create a task to continuously send quote updates to the client
        send_task = asyncio.create_task(send_quote_updates(websocket))
        
        async for message in websocket:
            await handle_websocket_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    finally:
        # Cancel the send task when the connection is closed
        send_task.cancel()

async def send_quote_updates(websocket):
    while True:
        try:
            quote = await quote_queue.get()
            await websocket.send(json.dumps(quote))
        except Exception as e:
            logging.error(f"Error sending quote update: {e}")
            # If there's an error, wait a bit before trying again
            await asyncio.sleep(1)

async def handle_websocket_message(websocket, message):
    data = json.loads(message)
    if "action" in data:
        if data["action"] == "unsubscribe":
            for symbol in data["symbols"]:
                # Unsubscribe logic for Dhan API
                print(f"Unsubscribed from {symbol}")
                logging.info(f"Unsubscribed from {symbol}")
        elif data["action"] == "subscribe":
            for symbol in data["symbols"]:
                # Subscribe logic for Dhan API
                print(f"Subscribed to {symbol}")
                logging.info(f"Subscribed to {symbol}")

            # Add a small delay after subscribing
            await asyncio.sleep(0.1)

            # Check for any pending quote updates
            while not quote_queue.empty():
                quote = await quote_queue.get()
                await websocket.send(json.dumps(quote))
    else:
        # Handle the existing credential update logic
        global client_id, access_token
        client_id = data.get("client_id", "")
        access_token = data.get("access_token", "")
        print(f"Updated credentials: {client_id[:5]}..., {access_token[:5]}...")

async def main():
    global loop
    loop = asyncio.get_running_loop()

    try:
        # Wait for valid credentials and security IDs
        logging.info("Waiting for valid data...")
        accessToken, clientId, instruments, subscription_code = await wait_for_data()
        logging.info(
            f"Using accessToken: {accessToken[:5]}..., clientId: {clientId}, instruments: {instruments}, subscription_code: {subscription_code}"
        )

        # Set up Dhan market feed connection
        feed = marketfeed.DhanFeed(
            clientId,
            accessToken,
            instruments,
            subscription_code,
            on_connect=on_connect,
            on_message=on_message,
        )

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8767)
        await server.wait_closed()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())