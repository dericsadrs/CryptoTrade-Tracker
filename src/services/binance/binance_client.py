import json
from binance.client import Client
from services.googlesheet_handler import GoogleSheetHandler
import logging
from google_sheet_config import Worksheet
from config import config_instance

logger = logging.getLogger(__name__)

class BinanceClient:
    """
    A client for interacting with the Binance API.
    """

    TRADING_STATUS = 'TRADING'  # Constant for trading status

    def __init__(self):
        """
        Initializes the BinanceClient with API keys from the configuration.
        """
        self.client = Client(
            config_instance.get_binance_api_key(),
            config_instance.get_binance_secret_key()
        )

    def clean_asset_name(self, asset: str) -> str:
        """Remove LD prefix and handle special cases."""
        logger.info(f"Asset before cleaning: {asset}")
        if asset.startswith('LD'):
            return asset[2:]  # Remove 'LD' prefix
        return asset

    def fetch_trading_pairs(self, assets: list) -> list:
        """
        Retrieves trading pairs available for the specified assets.
        """
        exchange_info = self.client.get_exchange_info()
        cleaned_assets = set(self.clean_asset_name(asset.upper()) for asset in assets)
        
        return [
            symbol_info['symbol'] for symbol_info in exchange_info['symbols']
            if (symbol_info['baseAsset'] in cleaned_assets and 
                symbol_info['quoteAsset'] in cleaned_assets and
                symbol_info['status'] == self.TRADING_STATUS)
        ]

    def get_trade_history(self, symbol: str) -> list:
        """
        Fetches the trade history for a specific trading symbol.
        """
        try:
            cleaned_symbol = self.clean_asset_name(symbol)
            trades = self.client.get_my_trades(symbol=cleaned_symbol)
            print(json.dumps(trades, indent=4))
            return trades
        except Exception as e:
            logger.error(f"Error fetching trades for {symbol}: {str(e)}")
            return []

