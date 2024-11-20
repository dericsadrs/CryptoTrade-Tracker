# config.py
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.binance_api_key = os.getenv("BINANCE_API_KEY")
        self.binance_secret_key = os.getenv("BINANCE_SECRET_KEY")

    def get_coingecko_api_key(self):
        return self.coingecko_api_key
    
    def get_binance_api_key(self):
        return self.binance_api_key
    
    def get_binance_secret_key(self):
        return self.binance_secret_key

# Create a single instance of Config
config_instance = Config()