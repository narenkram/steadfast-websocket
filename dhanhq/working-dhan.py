import asyncio
import websockets
import json
import logging
from dhanhq import marketfeed

logging.basicConfig(level=logging.DEBUG)

# Add your Dhan Client ID and Access Token
client_id = "1000588551"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzIzMzE3NjQzLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTAwMDU4ODU1MSJ9.-wEnKfQlLD3A8kiPj34E9Ck-5MLEJOMMAjQAyHBUsaNiT3nJNIQzXuZlrKXgwYqJuZcAvNbvrQ_7gffaENFNrA"

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

feed = marketfeed.DhanFeed(client_id,
    access_token,
    instruments,
    subscription_code,
    on_connect=on_connect,
    on_message=on_message)

async def websocket_server(websocket, path):
    try:
        async for message in websocket:
            print(f"Received message: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")

async def main():
    try:
        # Ensure the DhanFeed connection is awaited
        await feed.connect()

        # Set up WebSocket server
        server = await websockets.serve(websocket_server, "localhost", 8767)
        await server.wait_closed()
    except Exception as e:
        logging.error(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())