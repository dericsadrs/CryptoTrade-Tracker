from pybit.unified_trading import HTTP
from config import config_instance

class BybitClient:
    """
    A client for interacting with the Bybit API.
    """

    def __init__(self):
        """
        Initializes the BybitClient with API keys from the configuration.
        """
        self.api_key = config_instance.get_bybit_api_key()
        self.secret_key = config_instance.get_bybit_secret_key()
        self.client = self.create_session()

    def create_session(self):
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
            print("Bybit session successfully created.")
            return session
        except Exception as e:
            print(f"Error creating Bybit session: {e}")
            return None
    def get_wallet_balance(self):
        # Get wallet balance of the Unified Trading Account
        print(self.client.get_wallet_balance(accountType="UNIFIED"))
