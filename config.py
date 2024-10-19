import os

# Determine the environment
ENV = os.getenv("ENV", "production")

if ENV == "production":
    # Production settings
    BASE_URL = "https://api.steadfastapp.in"
else:
    # Development settings
    BASE_URL = "http://localhost:3000"

# API Endpoints
FLATTRADE_WEBSOCKET_DATA_ENDPOINT = f"{BASE_URL}/flattrade/websocketData"
SHOONYA_WEBSOCKET_DATA_ENDPOINT = f"{BASE_URL}/shoonya/websocketData"

# WebSocket server settings
WS_HOST = "0.0.0.0"  # Listen on all available interfaces
FLATTRADE_WS_PORT = 8765
SHOONYA_WS_PORT = 8766
