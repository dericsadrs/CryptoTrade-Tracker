import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from config import config_instance
# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceAuth:
    def __init__(self):
        self.api_key = config_instance.get_binance_api_key()
        self.api_secret = config_instance.get_binance_secret_key()
        self.base_url = 'https://api.binance.com'

    def _generate_signature(self, params):
        """Generate a signature for the given parameters."""
        query_string = urlencode(params)
        return hmac.new(
            self.api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_account_info(self):
        """Fetch account information from Binance API."""
        try:
            logger.info("Fetching account information...")
            endpoint = '/api/v3/account'
            timestamp = int(time.time() * 1000)

            params = {
                'timestamp': timestamp
            }

            params['signature'] = self._generate_signature(params)
            headers = {
                'X-MBX-APIKEY': self.api_key
            }

            response = requests.get(
                f"{self.base_url}{endpoint}",
                params=params,
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"Error getting account info. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []

            account_data = response.json()
            return account_data['balances']

        except Exception as e:
            logger.error(f"An error occurred while fetching account info: {str(e)}")
            return []
