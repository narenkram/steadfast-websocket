import requests
import asyncio
import websockets
import json
from dhanhq import marketfeed
import logging

logging.basicConfig(level=logging.DEBUG)

async def get_credentials():
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: requests.get("http://localhost:3000/dhan-websocket-data")
        )
        response.raise_for_status()
        data = response.json()
        logging.debug(f"Received data: {data}")
        client_id = data.get("clientId", "")
        access_token = data.get("accessToken", "")

        if client_id and access_token:
            logging.info("Valid data retrieved successfully")
            return client_id, access_token
        else:
            logging.info("Waiting for valid data...")
            return None, None
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to retrieve data: {e}")
        return None, None

async def wait_for_data():
    while True:
        client_id, access_token = await get_credentials()
        if client_id and access_token:
            return client_id, access_token
        await asyncio.sleep(5)  # Wait for 5 seconds before trying again

async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)
    await quote_queue.put(message)

quote_queue = asyncio.Queue()

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
                # Unsubscribe logic here
                print(f"Unsubscribed from {symbol}")
                logging.info(f"Unsubscribed from {symbol}")
        elif data["action"] == "subscribe":
            for symbol in data["symbols"]:
                # Subscribe logic here
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
        client_id = data.get("clientId", "")
        access_token = data.get("accessToken", "")
        print(f"Updated credentials: {client_id}, {access_token[:5]}...")

async def main():
    global loop
    loop = asyncio.get_running_loop()

    try:
        # Wait for valid credentials
        logging.info("Waiting for valid data...")
        client_id, access_token = await wait_for_data()
        logging.info(f"Using client_id: {client_id}, access_token: {access_token[:5]}...")

        exchange_segment = 0
        security_id = "25"
        instruments = [(exchange_segment, security_id)]
        subscription_code = marketfeed.Ticker

        print("Subscription code :", subscription_code)

        feed = marketfeed.DhanFeed(
            client_id,
            access_token,
            instruments,
            subscription_code,
            on_connect=on_connect,
            on_message=on_message
        )

        # Start the feed in a separate task
        asyncio.create_task(feed.run_forever())

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8767)
        await server.wait_closed()

    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())