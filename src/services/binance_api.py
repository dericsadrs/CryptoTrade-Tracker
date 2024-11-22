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
            
            # Clean asset names and convert to set
            cleaned_assets = set(clean_asset_name(asset.upper()) for asset in assets)
            logger.info(f"Cleaned assets looking for pairs: {cleaned_assets}")
            
            for symbol_info in exchange_info['symbols']:
                base_asset = symbol_info['baseAsset']
                quote_asset = symbol_info['quoteAsset']
                
                if (base_asset in cleaned_assets and quote_asset in cleaned_assets):
                    if symbol_info['status'] == 'TRADING':
                        valid_pairs.append(symbol_info['symbol'])
                        logger.info(f"Found valid trading pair: {symbol_info['symbol']}")

            return valid_pairs

        except Exception as e:
            logger.error(f"An error occurred while fetching trading pairs: {str(e)}")
            return []

    def get_trade_history(self, symbol):
        """Fetch trade history for a specific trading pair."""
        try:
            logger.info(f"Fetching trade history for {symbol}...")
            endpoint = '/api/v3/myTrades'
            timestamp = int(time.time() * 1000)

            params = {
                'symbol': symbol,
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
                logger.error(f"Error getting trade history for {symbol}. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return []

            return response.json()

        except Exception as e:
            logger.error(f"An error occurred while fetching trade history for {symbol}: {str(e)}")
            return []

    def get_all_trades(self):
        """Fetch trade history for all available trading pairs."""
        all_trades = []
        trading_pairs = self.get_trading_pairs_for_assets(self.get_account_info())
        
        for pair in trading_pairs:
            trades = self.get_trade_history(pair)
            all_trades.extend(trades)
            time.sleep(0.1)  # Rate limiting to avoid hitting API limits
            
        return all_trades