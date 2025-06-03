import time
import logging
from pybit.unified_trading import HTTP
from config import config_instance

logger = logging.getLogger(__name__)

class BybitClient:
    """
    Bybit V5 API client implementation for spot trading.
    """

    def __init__(self):
        """
        Initialize Bybit client with API credentials.
        """
        self.client = HTTP(
            api_key=config_instance.get_bybit_api_key(),
            api_secret=config_instance.get_bybit_secret_key(),
            testnet=False  # Set to True for testing
        )
        self.last_request_time = 0

    def _rate_limit_check(self):
        """Rate limiting for Bybit API"""
        current_time = time.time()
        if current_time - self.last_request_time < 0.12:  # 120ms between requests
            time.sleep(0.12)
        self.last_request_time = current_time

    def get_account_balance(self):
        """
        Get account wallet balance.
        
        Returns:
            dict: Account balance information
        """
        try:
            self._rate_limit_check()
            response = self.client.get_wallet_balance(
                accountType="UNIFIED"  # or "SPOT" for classic account
            )
            
            if response['retCode'] == 0:
                return response['result']
            else:
                logger.error(f"Bybit API error: {response['retMsg']}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting Bybit account balance: {e}")
            return {}

    def get_instruments_info(self, category="spot"):
        """
        Get trading instruments information.
        
        Args:
            category (str): Product category (spot, linear, inverse, option)
            
        Returns:
            list: List of available instruments
        """
        try:
            self._rate_limit_check()
            response = self.client.get_instruments_info(category=category)
            
            if response['retCode'] == 0:
                return response['result']['list']
            else:
                logger.error(f"Bybit API error: {response['retMsg']}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Bybit instruments: {e}")
            return []

    def get_execution_history(self, category="spot", symbol=None, limit=50):
        """
        Get trade execution history using V5 API.
        
        Args:
            category (str): Product category (spot, linear, inverse, option)
            symbol (str): Trading symbol (optional)
            limit (int): Number of records (max 100)
            
        Returns:
            list: List of trade executions
        """
        try:
            self._rate_limit_check()
            
            params = {
                "category": category,
                "limit": min(limit, 100)  # API max is 100
            }
            
            if symbol:
                params["symbol"] = symbol
                
            response = self.client.get_executions(**params)
            
            if response['retCode'] == 0:
                logger.info(f"Retrieved {len(response['result']['list'])} executions")
                return response['result']['list']
            else:
                logger.error(f"Bybit API error: {response['retMsg']}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Bybit execution history: {e}")
            return []

    def get_all_spot_trades(self, limit=50):
        """
        Get all spot trading history for the account.
        
        Args:
            limit (int): Trades per request
            
        Returns:
            list: All spot trades
        """
        all_trades = []
        next_page_cursor = None
        
        try:
            while True:
                self._rate_limit_check()
                
                params = {
                    "category": "spot",
                    "limit": min(limit, 100)
                }
                
                if next_page_cursor:
                    params["cursor"] = next_page_cursor
                
                response = self.client.get_executions(**params)
                
                if response['retCode'] == 0:
                    trades = response['result']['list']
                    all_trades.extend(trades)
                    
                    # Check for next page
                    next_page_cursor = response['result'].get('nextPageCursor')
                    if not next_page_cursor:
                        break
                        
                    logger.info(f"Fetched {len(trades)} trades, continuing...")
                    
                else:
                    logger.error(f"Bybit API error: {response['retMsg']}")
                    break
                    
        except Exception as e:
            logger.error(f"Error getting all Bybit trades: {e}")
            
        logger.info(f"Total Bybit trades collected: {len(all_trades)}")
        return all_trades

    def get_symbols_with_trades(self):
        """
        Get symbols that have trading history.
        
        Returns:
            set: Set of symbols with trades
        """
        try:
            trades = self.get_all_spot_trades(limit=100)
            symbols = set(trade['symbol'] for trade in trades if 'symbol' in trade)
            logger.info(f"Found {len(symbols)} symbols with trades")
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting symbols with trades: {e}")
            return set()
