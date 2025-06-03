import json
import time
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
import logging
from config import config_instance

logger = logging.getLogger(__name__)

class BinanceClient:
    """
    Enhanced Binance client with proper error handling and API best practices.
    """

    def __init__(self):
        """
        Initializes the BinanceClient with API keys from configuration.
        """
        self.client = Client(
            config_instance.get_binance_api_key(),
            config_instance.get_binance_secret_key()
        )
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit_check(self):
        """Basic rate limiting to prevent API abuse"""
        current_time = time.time()
        if current_time - self.last_request_time < 0.1:  # 100ms between requests
            time.sleep(0.1)
        self.last_request_time = current_time

    def get_account_balances(self):
        """
        Get account balances with non-zero holdings.
        
        Returns:
            list: List of assets with non-zero balances
        """
        try:
            self._rate_limit_check()
            account = self.client.get_account()
            return [
                b['asset'] for b in account['balances'] 
                if float(b['free']) > 0 or float(b['locked']) > 0
            ]
        except BinanceAPIException as e:
            logger.error(f"Binance API error getting balances: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting balances: {e}")
            return []

    def get_all_trading_symbols(self):
        """
        Get all active trading symbols from exchange info.
        
        Returns:
            list: List of all active trading symbols
        """
        try:
            self._rate_limit_check()
            exchange_info = self.client.get_exchange_info()
            return [
                symbol_info['symbol'] for symbol_info in exchange_info['symbols']
                if symbol_info['status'] == 'TRADING'
            ]
        except BinanceAPIException as e:
            logger.error(f"Binance API error getting exchange info: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting exchange info: {e}")
            return []

    def get_symbols_for_assets(self, assets):
        """
        Get trading symbols that involve the user's assets.
        More efficient approach than the original method.
        
        Args:
            assets (list): List of user's assets
            
        Returns:
            list: List of relevant trading symbols
        """
        try:
            self._rate_limit_check()
            exchange_info = self.client.get_exchange_info()
            user_assets = set(asset.upper() for asset in assets)
            
            relevant_symbols = []
            for symbol_info in exchange_info['symbols']:
                if (symbol_info['status'] == 'TRADING' and 
                    (symbol_info['baseAsset'] in user_assets or 
                     symbol_info['quoteAsset'] in user_assets)):
                    relevant_symbols.append(symbol_info['symbol'])
            
            logger.info(f"Found {len(relevant_symbols)} relevant symbols for assets")
            return relevant_symbols
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error getting symbols: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error getting symbols: {e}")
            return []

    def get_trade_history(self, symbol, limit=1000):
        """
        Fetches trade history for a specific symbol using official API.
        
        Args:
            symbol (str): Trading symbol
            limit (int): Number of trades to fetch (max 1000)
            
        Returns:
            list: List of trades for the symbol
        """
        try:
            self._rate_limit_check()
            # Use official myTrades endpoint
            trades = self.client.get_my_trades(symbol=symbol, limit=limit)
            logger.info(f"Retrieved {len(trades)} trades for {symbol}")
            return trades
            
        except BinanceAPIException as e:
            if e.code == -1121:  # Invalid symbol
                logger.warning(f"Invalid symbol {symbol}, skipping")
                return []
            else:
                logger.error(f"Binance API error for {symbol}: {e}")
                return []
        except Exception as e:
            logger.error(f"Unexpected error fetching trades for {symbol}: {e}")
            return []

    def get_recent_trades_batch(self, symbols, limit=500):
        """
        Efficiently fetch recent trades for multiple symbols.
        
        Args:
            symbols (list): List of trading symbols
            limit (int): Trades per symbol
            
        Returns:
            list: All trades from all symbols
        """
        all_trades = []
        
        for symbol in symbols:
            try:
                trades = self.get_trade_history(symbol, limit)
                all_trades.extend(trades)
                
                # Respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error processing {symbol}: {e}")
                continue
                
        logger.info(f"Total trades collected: {len(all_trades)}")
        return all_trades
