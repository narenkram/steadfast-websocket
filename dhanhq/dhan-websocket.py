import asyncio
import websockets
import json
import logging
import aiohttp  # Add this import
from marketfeed import DhanFeed, Ticker

logging.basicConfig(level=logging.DEBUG)

# Function to fetch credentials and subscription details from the server
async def fetch_credentials():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:3000/dhan-websocket-data') as response:
            if response.status == 200:
                data = await response.json()
                return data['clientId'], data['accessToken'], data['exchangeSegment'], data['securityId']
            else:
                logging.error(f"Failed to fetch credentials: {response.status}")
                return None, None, None, None

# Type of data subscription
subscription_code = Ticker

async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)

print("Subscription code :", subscription_code)

async def websocket_server(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

async def main():
    try:
        # Fetch credentials and subscription details from the server
        client_id, access_token, exchange_segment, security_id = await fetch_credentials()
        if not client_id or not access_token or exchange_segment is None or security_id is None:
            logging.error("Missing client_id, access_token, exchange_segment, or security_id")
            return

        instruments = [(str(exchange_segment), str(security_id))]  # Ensure these are strings

        feed = DhanFeed(client_id,
            access_token,
            instruments,
            subscription_code,
            on_connect=on_connect,
            on_message=on_message)

        # Initialize the event loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError as e:
            if str(e).startswith('There is no current event loop in thread'):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            else:
                raise

        # Ensure the DhanFeed connection is awaited
        await feed.connect()

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8767)
        await server.wait_closed()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())