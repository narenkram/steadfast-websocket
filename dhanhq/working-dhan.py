import asyncio
import websockets
import json
import logging
import aiohttp  # Add this import
from dhanhq import marketfeed

logging.basicConfig(level=logging.DEBUG)

# Function to fetch credentials from the server
async def fetch_credentials():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://localhost:3000/dhan-websocket-data') as response:
            if response.status == 200:
                data = await response.json()
                return data['clientId'], data['accessToken']
            else:
                logging.error(f"Failed to fetch credentials: {response.status}")
                return None, None

# Structure for subscribing is ("exchange_segment","security_id")
exchange_segment = 0
security_id = "25"
instruments = [(exchange_segment, security_id)]

# Type of data subscription
subscription_code = marketfeed.Ticker

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
        # Fetch credentials from the server
        client_id, access_token = await fetch_credentials()
        if not client_id or not access_token:
            logging.error("Missing client_id or access_token")
            return

        feed = marketfeed.DhanFeed(client_id,
            access_token,
            instruments,
            subscription_code,
            on_connect=on_connect,
            on_message=on_message)

        # Ensure the DhanFeed connection is awaited
        await feed.connect()

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8767)
        await server.wait_closed()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())