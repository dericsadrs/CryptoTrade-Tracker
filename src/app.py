from services.binance.binance_trade_history import BinanceTradeHistory
from services.googlesheet_handler import GoogleSheetHandler
from services.helpers import clean_asset_name
import logging
from google_sheet_config import Worksheet

logger = logging.getLogger(__name__)

def get_available_pairs():
    client = BinanceTradeHistory()
    balances = client.auth.get_account_info()

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
        logger.info(f"Retrieved {len(trades)} trades for {pair}")
    return all_trades

def main():
    try:
        # Initialize Google Sheet handler
        sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
        
        # Get available trading pairs
        available_pairs = get_available_pairs()
        logger.info(f"Available trading pairs: {available_pairs}")

        # Get trade history
        trades = get_trade_history_for_pairs()
        logger.info(f"Retrieved total of {len(trades)} trades")
        
        # Write trades to Google Sheet
        sheet_handler.write_trades(trades)
        logger.info("Successfully wrote trades to Google Sheet")
        
        return trades

    except Exception as e:
        logger.error(f"An error occurred in main: {str(e)}")
        return []

if __name__ == "__main__":
    main()