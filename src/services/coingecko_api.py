import requests
import logging
from config import config_instance  # Import the config instance

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - [CoinGeckoAPI] - %(message)s')
logger = logging.getLogger(__name__)

class CoinGeckoAPI:
    BASE_URL = "https://api.coingecko.com/api/v3"

    def __init__(self):
        self.api_key = config_instance.get_coingecko_api_key()  # Use the imported instance
        self.headers = {
            "accept": "application/json",
            "x-cg-demo-api-key": self.api_key
        }
        logger.info("CoinGeckoAPI initialized with API key.")

    def ping(self):
        """Check the API server status."""
        logger.debug("Sending ping request to CoinGecko API.")
        response = requests.get(f"{self.BASE_URL}/ping", headers=self.headers)
        logger.info("Ping response received.")
        return response.json()

    def get_price(self, coin_ids, currency='usd'):
        """Fetch the current price of one or more coins."""
        logger.debug(f"Fetching price for coins: {coin_ids} in {currency}.")
        url = f"{self.BASE_URL}/simple/price"
        params = {
            'ids': coin_ids,
            'vs_currencies': currency
        }
        response = requests.get(url, headers=self.headers, params=params)
        logger.info("Price response received.")
        return response.json()

    def get_coins_list(self):
        """Fetch the list of all supported coins."""
        logger.debug("Fetching list of supported coins.")
        response = requests.get(f"{self.BASE_URL}/coins/list", headers=self.headers)
        logger.info("Coins list response received.")
        return response.json()

    def get_coin_data(self, coin_id):
        """Fetch detailed data for a specific coin."""
        logger.debug(f"Fetching data for coin: {coin_id}.")
        url = f"{self.BASE_URL}/coins/{coin_id}"
        response = requests.get(url, headers=self.headers)
        logger.info("Coin data response received.")
        return response.json()

    def get_market_data(self, coin_id):
        """Fetch market data for a specific coin."""
        logger.debug(f"Fetching market data for coin: {coin_id}.")
        url = f"{self.BASE_URL}/coins/{coin_id}/markets"
        response = requests.get(url, headers=self.headers)
        logger.info("Market data response received.")
        return response.json()
