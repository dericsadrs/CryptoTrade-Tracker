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

    def get_all_trades(self):
        """Fetch all trades for the account."""
        try:
            logger.info("Starting trade fetch process...")
            balances = self.get_account_info()

            # Clean up asset names by removing LD prefix
            assets = [clean_asset_name(b['asset']) for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
            logger.info(f"Found assets (after cleaning): {', '.join(assets)}")

            # Common trading pairs format
            trading_pairs = [f"{asset}USDT" for asset in assets if asset != 'USDT']
            logger.info(f"Checking trading pairs: {', '.join(trading_pairs)}")

            all_trades = []
            for pair in trading_pairs:
                logger.info(f"Fetching trades for {pair}...")
                try:
                    timestamp = int(time.time() * 1000)
                    params = {
                        'symbol': pair,
                        'timestamp': timestamp,
                        'limit': 1000
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

                    trades_response = requests.get(
                        f"{self.base_url}/api/v3/myTrades",
                        params=params,
                        headers=headers
                    )

                    if trades_response.status_code == 200:
                        symbol_trades = trades_response.json()
                        if symbol_trades:
                            logger.info(f"Found {len(symbol_trades)} trades for {pair}")
                            all_trades.extend(symbol_trades)
                    else:
                        logger.warning(f"Failed to get trades for {pair}. Status code: {trades_response.status_code}")
                        logger.warning(f"Response: {trades_response.text}")

                except Exception as e:
                    logger.error(f"Error processing {pair}: {str(e)}")
                    continue

                time.sleep(0.1)  # Rate limiting

            logger.info(f"Total trades found: {len(all_trades)}")
            return all_trades

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return []

    def get_market_data(self, ticker):
        """Fetch market data for a specific coin with 'LT' prefix."""
        try:

            endpoint = f"/api/v3/ticker/24hr?symbol={ticker}"  # Assuming you want the market data against USDT
            logger.info(f"Fetching market data for {ticker}...")

            response = requests.get(f"{self.base_url}{endpoint}")

            if response.status_code == 200:
                market_data = response.json()
                logger.info(f"Market data for {ticker}: {market_data}")
                return market_data
            else:
                logger.error(f"Error fetching market data. Status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None

        except Exception as e:
            logger.error(f"An error occurred while fetching market data: {str(e)}")
            return None
