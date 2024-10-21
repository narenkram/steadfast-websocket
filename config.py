import os

# Determine the environment
ENV = os.getenv("ENV", "development")

if ENV == "production":
    # Production settings
    BASE_URL = "https://api.steadfastapp.in"
    FLATTRADE_WS_PORT = int(os.getenv("FLATTRADE_WS_PORT", 8765))
    SHOONYA_WS_PORT = int(os.getenv("SHOONYA_WS_PORT", 8766))
elif ENV == "development":
    # Development settings
    BASE_URL = "http://localhost:3000"
    FLATTRADE_WS_PORT = int(os.getenv("FLATTRADE_WS_PORT", 8765))
    SHOONYA_WS_PORT = int(os.getenv("SHOONYA_WS_PORT", 8766))
else:
    raise ValueError(f"Invalid environment: {ENV}")

# API Endpoints
FLATTRADE_WEBSOCKET_DATA_ENDPOINT = f"{BASE_URL}/flattrade/websocketData"
SHOONYA_WEBSOCKET_DATA_ENDPOINT = f"{BASE_URL}/shoonya/websocketData"

# WebSocket server settings
WS_HOST = "0.0.0.0"  # Listen on all available interfaces
