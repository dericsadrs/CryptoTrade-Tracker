# config.py
import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")

    def get_coingecko_api_key(self):
        return self.coingecko_api_key

# Create a single instance of Config
config_instance = Config()