from dhanhq import marketfeed

# Add your Dhan Client ID and Access Token

# Structure for subscribing is ("exchange_segment","security_id")

# Maximum 100 instruments can be subscribed, then use 'subscribe_symbols' function 

exchange_segment = 0
security_id = "25"

instruments = [(exchange_segment, security_id)]

# Type of data subscription
subscription_code = marketfeed.Ticker

# Ticker - Ticker Data
# Quote - Quote Data
# Depth - Market Depth


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

feed.run_forever()