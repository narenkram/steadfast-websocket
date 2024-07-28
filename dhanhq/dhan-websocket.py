import asyncio
import websockets
import json
import logging
import aiohttp  # Add this import
from marketfeed import DhanFeed, Ticker

logging.basicConfig(level=logging.DEBUG)

# Function to fetch credentials and subscription details from the server
async def fetch_credentials():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000/dhan-websocket-data') as response:
                if response.status == 200:
                    data = await response.json()
                    return data['clientId'], data['accessToken'], data['exchangeSegment'], data['securityId']
                else:
                    logging.error(f"Failed to fetch credentials: {response.status}")
                    return None, None, None, None
    except aiohttp.ClientError as e:
        logging.error(f"Failed to retrieve data: {e}")
        return None, None, None, None

async def wait_for_data():
    while True:
        client_id, access_token, exchange_segment, security_id = await fetch_credentials()
        if client_id and access_token and exchange_segment is not None and security_id is not None:
            return client_id, access_token, exchange_segment, security_id
        await asyncio.sleep(5)  # Wait for 5 seconds before trying again

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
        # Wait for valid credentials and subscription details from the server
        logging.info("Waiting for valid data...")
        client_id, access_token, exchange_segment, security_id = await wait_for_data()
        logging.info(f"Using client_id: {client_id[:5]}..., access_token: {access_token[:5]}..., exchange_segment: {exchange_segment}, security_id: {security_id}")

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