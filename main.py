import asyncio
from dotenv import load_dotenv
from flattrade.flattrade_websocket import main as flattrade_main
from shoonya.shoonya_websocket import main as shoonya_main

# Load environment variables from .env file
load_dotenv()

async def main():
    await asyncio.gather(flattrade_main(), shoonya_main())

if __name__ == "__main__":
    asyncio.run(main())
