import json
from services.binance.binance_client import BinanceClient
from services.googlesheet_handler import GoogleSheetHandler
import logging
from google_sheet_config import Worksheet
from services.bybit.bybit_client import BybitClient
logger = logging.getLogger(__name__)

def get_binance_trades():
    """
    Fetches all trades from Binance for available trading pairs.

    Returns:
        list: List of all trades from Binance.
    """
    client = BinanceClient()
    try:
        # Get account balances to determine assets
        account = client.client.get_account()
        assets = [b['asset'] for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        
        # Retrieve trading pairs
        available_pairs = client.get_trading_pairs_for_assets(assets)
        logger.info(f"Available trading pairs: {available_pairs}")
        
        # Retrieve trades for each pair
        all_trades = []
        for pair in available_pairs:
            trades = client.get_trade_history(pair)
            all_trades.extend(trades)
            logger.info(f"Retrieved {len(trades)} trades for {pair}")
        
        return all_trades
    except Exception as e:
        logger.error(f"Error fetching Binance trades: {str(e)}")
        return []
def main():
    try:
        sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
        trades = get_binance_trades()
        sheet_handler.write_trades(trades)
        return trades
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return []

if __name__ == "__main__":
    client = BybitClient()
    
    print(client.client)  # Verify session object
    print(client.get_wallet_balance())  # Verify wallet balance
    