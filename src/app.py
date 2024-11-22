from services.binance.binance_trade_history import BinanceTradeHistory
from services.helpers import clean_asset_name
from config import config_instance
import logging

logger = logging.getLogger(__name__)

def get_available_pairs():
    client = BinanceTradeHistory()  # Updated to use BinanceTradeHistory
    balances = client.auth.get_account_info()  # Accessing account info through auth

    assets = [clean_asset_name(b['asset']) for b in balances 
             if float(b['free']) > 0 or float(b['locked']) > 0]
    trading_pairs = client.get_trading_pairs_for_assets(assets)
    return trading_pairs

def get_trade_history_for_pairs():
    client = BinanceTradeHistory()
    available_pairs = get_available_pairs()
    
    all_trades = []
    for pair in available_pairs:
        trades = client.get_trade_history(pair)
        all_trades.extend(trades)
    return all_trades

def main():
    try:
        # Get available trading pairs
        available_pairs = get_available_pairs()
        logger.info(f"Available trading pairs: {available_pairs}")

        # Get trade history
        trades = get_trade_history_for_pairs()
        logging.info(f"Trades: {trades}")
        logger.info(f"Retrieved {len(trades)} trades")
        
        return trades

    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}")
        return []

if __name__ == "__main__":
    main()