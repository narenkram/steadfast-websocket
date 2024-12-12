import os
import asyncio
import json
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

IPC_PORT = 5000  # Same port as in Node.js server


class BrokerSelector:
    def __init__(self):
        self.selected_broker = None
        print("BrokerSelector initialized")

    async def handle_client(self, reader, writer):
        print("New client connection received")
        data = await reader.read(100)
        message = data.decode()
        addr = writer.get_extra_info("peername")

        print(f"Received {message!r} from {addr!r}")

        try:
            parsed_message = json.loads(message)
            if parsed_message["action"] == "set_broker":
                self.selected_broker = parsed_message["broker"]
                print(f"Broker set to: {self.selected_broker}")
                response = json.dumps(
                    {
                        "status": "success",
                        "message": f"Broker set to {self.selected_broker}",
                    }
                )
                writer.write(response.encode())
                await writer.drain()
        except json.JSONDecodeError:
            print("Received invalid JSON")
            response = json.dumps(
                {"status": "error", "message": "Invalid JSON received"}
            )
            writer.write(response.encode())
            await writer.drain()

        writer.close()
        await writer.wait_closed()

    async def start_ipc_server(self):
        try:
            server = await asyncio.start_server(
                self.handle_client, 
                '127.0.0.1',
                IPC_PORT
            )
            addr = server.sockets[0].getsockname()
            print(f"IPC Server running on {addr}")

            async with server:
                await server.serve_forever()
        except Exception as e:
            print(f"Error starting IPC server: {e}")


async def main():
    try:
        broker_selector = BrokerSelector()
        
        # Start the IPC server and store the task
        ipc_server_task = asyncio.create_task(broker_selector.start_ipc_server())
        
        print("WebSocket server starting...")
        print("Waiting for broker selection...")
        
        while not broker_selector.selected_broker:
            await asyncio.sleep(1)
            print("Waiting for broker selection...")

        selected_broker = broker_selector.selected_broker
        print(f"Selected broker: {selected_broker}")

        ws_port = BROKER_PORTS[selected_broker]
        print(f"Starting {selected_broker.capitalize()} WebSocket on port {ws_port}...")

        if selected_broker == "flattrade":
            flattrade_initialize_api()
            await flattrade_main(ws_port)
        elif selected_broker == "shoonya":
            shoonya_initialize_api()
            await shoonya_main(ws_port)

    except Exception as e:
        print(f"Error in main: {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server shutting down...")
    except Exception as e:
        print(f"Fatal error: {e}")
