from datetime import datetime, timedelta
import time
from pybit.unified_trading import HTTP
from config import config_instance
import logging

logger = logging.getLogger(__name__)

class BybitClient:
    """
    A client for interacting with the Bybit API.
    """

    UNIFIED_ACCOUNT = "UNIFIED"
    SPOT = "SPOT"

    def __init__(self):
        """
        Initializes the BybitClient with API keys from the configuration.
        """
        self.api_key = config_instance.get_bybit_api_key()
        self.secret_key = config_instance.get_bybit_secret_key()
        self.client = self._create_session()

    def _create_session(self):
        """
        Creates a session for interacting with the Bybit API.
        
        Returns:
            HTTP: A session object for the Bybit Unified Trading API.
        """
        try:
            session = HTTP(
                testnet=False,
                api_key=self.api_key,
                api_secret=self.secret_key
            )
            logger.info("Bybit session successfully created.")
            return session
        except Exception as e:
            logger.error(f"Error creating Bybit session: {e}")
            return None

    def get_wallet_balance(self):
        """
        Retrieves the wallet balance of the Unified Trading Account.
        
        Returns:
            float: The wallet balance.
        """
        balance = self.client.get_wallet_balance(accountType=self.UNIFIED_ACCOUNT)
        logger.info(f"Wallet Balance: ${balance}")
        return balance

    def get_trade_history(self):
        
        try: 
            
                # Calculate timestamps for the last 180 days
            end_time = datetime.now()
            start_time = end_time - timedelta(days=180)

            # Convert to milliseconds
            end_time_ms = int(end_time.timestamp() * 1000)
            start_time_ms = int(start_time.timestamp() * 1000)

            # List to store results
            all_trades = []

            # Query in 7-day chunks
            chunk_duration = timedelta(days=7)
            chunk_start = start_time

            while chunk_start < end_time:
                chunk_end = chunk_start + chunk_duration
                if chunk_end > end_time:
                    chunk_end = end_time

                # Convert chunk times to milliseconds
                chunk_start_ms = int(chunk_start.timestamp() * 1000)
                chunk_end_ms = int(chunk_end.timestamp() * 1000)

                # Query the API for this chunk
                response = self.client.get_order_history(
                    category="spot",  # Only spot trades
                    startTime=chunk_start_ms,
                    endTime=chunk_end_ms
                )
                
                # Log the raw response
                logger.info(f"Raw Bybit API response: {response}")

                # Combine results
                if "result" in response and "list" in response["result"]:
                    all_trades.extend(response["result"]["list"])

                # Move to the next chunk
                chunk_start = chunk_end

            return all_trades

        except Exception as e:
            logger.error(f"Error fetching Bybit trades: {e}")
            raise