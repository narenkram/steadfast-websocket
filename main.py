import os
import asyncio
from dotenv import load_dotenv
from flattrade.flattrade_websocket import (
    main as flattrade_main,
    initialize_api as flattrade_initialize_api,
)
from shoonya.shoonya_websocket import (
    main as shoonya_main,
    initialize_api as shoonya_initialize_api,
)

# Load environment variables from .env file
load_dotenv()

# Define broker-specific ports
BROKER_PORTS = {"flattrade": 8765, "shoonya": 8766}


async def main():
    selected_broker = os.getenv("SELECTED_BROKER", "flattrade").lower()
    print(f"Selected broker from environment: {selected_broker}")

    if selected_broker in BROKER_PORTS:
        ws_port = BROKER_PORTS[selected_broker]
        print(f"Starting {selected_broker.capitalize()} WebSocket on port {ws_port}...")

        if selected_broker == "flattrade":
            flattrade_initialize_api()
            await flattrade_main(ws_port)
        elif selected_broker == "shoonya":
            shoonya_initialize_api()
            await shoonya_main(ws_port)
    else:
        print(
            f"Invalid broker '{selected_broker}' selected. Using default broker 'flattrade'."
        )
        ws_port = BROKER_PORTS["flattrade"]
        print(f"Starting Flattrade WebSocket on port {ws_port}...")
        flattrade_initialize_api()
        await flattrade_main(ws_port)


if __name__ == "__main__":
    asyncio.run(main())