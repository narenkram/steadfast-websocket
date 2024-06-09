from dhanhq import marketfeed
import asyncio
import redis
import json

# Add your Dhan Client ID and Access Token
client_id = "1000588551"
access_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzE4ODA4MzUwLCJ0b2tlbkNvbnN1bWVyVHlwZSI6IlNFTEYiLCJ3ZWJob29rVXJsIjoiIiwiZGhhbkNsaWVudElkIjoiMTAwMDU4ODU1MSJ9.dsOQ5uA9eP-2A0hUjHvwbUZ_3Cg2S_1Rr68oufBJkiDqsqvGqjrjWB_7h6sKUDEJGUMmt4UEuV-oDW-FzzvjXQ"

# Structure for subscribing is ("exchange_segment","security_id")
# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 
instruments = [("NSE_FNO", "1333"), ("BSE_FNO", "13")]

# Type of data subscription
subscription_code = marketfeed.Ticker

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth

# Initialize Redis client
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

async def on_connect(instance):
    print("Connected to websocket")

async def on_message(instance, message):
    print("Received:", message)
    # Publish message to Redis channel
    redis_client.publish('market_feed', json.dumps(message))

async def on_close(instance):
    print("Websocket closed.")

async def main():
    feed = marketfeed.DhanFeed(
        client_id=client_id,
        access_token=access_token,
        instruments=instruments,
        subscription_code=subscription_code,
        on_connect=on_connect,
        on_message=on_message,
        on_close=on_close
    )
    await feed.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
