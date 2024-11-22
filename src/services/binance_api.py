import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from services.helpers import clean_asset_name

# Set up logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BinanceAPI:
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = 'https://api.binance.com'

    def get_account_info(self):
        """Fetch account information from Binance API."""
        try:
            logger.info("Fetching account information...")
            endpoint = '/api/v3/account'
            timestamp = int(time.time() * 1000)

            params = {
                'timestamp': timestamp
            }

            query_string = urlencode(params)
            signature = hmac.new(
                self.api_secret.encode('utf-8'),
                query_string.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()

            params['signature'] = signature
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

    def get_trading_pairs_for_assets(self, assets):
        """
        Fetch only relevant trading pairs for given assets that exist in the account.
        This optimized version will only return pairs where either the base or quote asset
        is in the user's account with a non-zero balance.
        """
        try:
            logger.info("Fetching exchange information for account assets...")
            response = requests.get(f"{self.base_url}/api/v3/exchangeInfo")
            
            if response.status_code != 200:
                logger.error(f"Error getting exchange info. Status code: {response.status_code}")
                return []

            exchange_info = response.json()
            valid_pairs = []
            assets = set(asset.upper() for asset in assets)  # Convert to set for O(1) lookup
            
            logger.info(f"Filtering trading pairs for assets: {', '.join(assets)}")
            
            # Find trading pairs where BOTH base and quote assets are in our assets list
            for symbol_info in exchange_info['symbols']:
                base_asset = symbol_info['baseAsset']
                quote_asset = symbol_info['quoteAsset']
                
                # Only include pairs where we have both the base and quote assets
                if (base_asset in assets and quote_asset in assets):
                    if symbol_info['status'] == 'TRADING':  # Only include active trading pairs
                        valid_pairs.append(symbol_info['symbol'])
                        logger.info(f"Found valid trading pair: {symbol_info['symbol']}")

            logger.info(f"Total valid trading pairs found: {len(valid_pairs)}")
            return valid_pairs

        except Exception as e:
            logger.error(f"An error occurred while fetching trading pairs: {str(e)}")
            return []

   