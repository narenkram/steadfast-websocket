import os
import asyncio
from dotenv import load_dotenv
from flattrade.flattrade_websocket import main as flattrade_main
from shoonya.shoonya_websocket import main as shoonya_main

# Load environment variables from .env file
load_dotenv()

# Define broker-specific ports
BROKER_PORTS = {"flattrade": 8765, "shoonya": 8766}


async def main():
    selected_broker = os.getenv("SELECTED_BROKER", "").lower()
    print(f"Selected broker from environment: {selected_broker}")

    if selected_broker in BROKER_PORTS:
        ws_port = BROKER_PORTS[selected_broker]
        print(f"Starting {selected_broker.capitalize()} WebSocket on port {ws_port}...")

        if selected_broker == "flattrade":
            await flattrade_main(ws_port)
        elif selected_broker == "shoonya":
            await shoonya_main(ws_port)
    else:
        print(
            "No valid broker selected. Please set the SELECTED_BROKER environment variable to 'flattrade' or 'shoonya'."
        )


if __name__ == "__main__":
    asyncio.run(main())
