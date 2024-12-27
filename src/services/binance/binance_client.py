import json
from binance.client import Client
from services.googlesheet_handler import GoogleSheetHandler
from services.helpers import clean_asset_name
import logging
from google_sheet_config import Worksheet
from config import config_instance

logger = logging.getLogger(__name__)

class BinanceClient:
    """
    A client for interacting with the Binance API.
    """

    def __init__(self):
        """
        Initializes the BinanceClient with API keys from the configuration.
        """
        self.client = Client(
            config_instance.get_binance_api_key(),
            config_instance.get_binance_secret_key()
        )

    def get_trading_pairs_for_assets(self, assets):
        """
        Retrieves trading pairs available for the specified assets.

        Args:
            assets (list): A list of asset names to check for trading pairs.

        Returns:
            list: A list of trading pair symbols that are currently trading.
        """
        exchange_info = self.client.get_exchange_info()
        cleaned_assets = set(clean_asset_name(asset.upper()) for asset in assets)
        
        return [
            symbol_info['symbol'] for symbol_info in exchange_info['symbols']
            if (symbol_info['baseAsset'] in cleaned_assets and 
                symbol_info['quoteAsset'] in cleaned_assets and
                symbol_info['status'] == 'TRADING')
        ]

    def get_trade_history(self, symbol):
        """
        Fetches the trade history for a specific trading symbol.

        Args:
            symbol (str): The trading symbol to fetch the trade history for.

        Returns:
            list: A list of trades for the specified symbol, or an empty list if an error occurs.
        """
        try:
            trades = self.client.get_my_trades(symbol=symbol)
            # Pretty print the JSON response
            print(json.dumps(trades, indent=4))
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {str(e)}")
            return []

