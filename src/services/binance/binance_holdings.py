# services/binance/binance_holdings.py
import logging
from .binance_auth import BinanceAuth
from services.helpers import clean_asset_name

logger = logging.getLogger(__name__)

class BinanceHoldings:
    def __init__(self):
        self.auth = BinanceAuth()

    def get_current_holdings(self):
        """
        Get current holdings from Binance account.
        Returns list of assets with non-zero balances.
        """
        try:
            balances = self.auth.get_account_info()
            
            # Filter for non-zero balances and format
            holdings = []
            for balance in balances:
                total = float(balance['free']) + float(balance['locked'])
                if total > 0:
                    holdings.append({
                        'asset': clean_asset_name(balance['asset']),
                        'free': float(balance['free']),
                        'locked': float(balance['locked']),
                        'total': total
                    })
            
            logger.info(f"Retrieved {len(holdings)} assets with non-zero balance")
            return holdings
            
        except Exception as e:
            logger.error(f"Error fetching holdings: {str(e)}")
            return []