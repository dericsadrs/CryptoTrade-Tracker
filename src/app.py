import json
from services.binance.binance_client import BinanceClient
from services.googlesheet_handler import GoogleSheetHandler
from services.helpers import clean_asset_name
import logging
from google_sheet_config import Worksheet
from services.trade_mapping import map_binance_trade

logger = logging.getLogger(__name__)

def get_available_pairs():
    client = BinanceClient()
    account = client.client.get_account()
    
    assets = [clean_asset_name(b['asset']) for b in account['balances'] 
             if float(b['free']) > 0 or float(b['locked']) > 0]
    return client.get_trading_pairs_for_assets(assets)

def get_trade_history_for_pairs():
    client = BinanceClient()
    available_pairs = get_available_pairs()
    
    all_trades = []
    for pair in available_pairs:
        trades = client.get_trade_history(pair)
        all_trades.extend(trades)
        logger.info(f"Retrieved {len(trades)} trades for {pair}")
    return all_trades

def main():
    try:
        sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
        available_pairs = get_available_pairs()
        trades = get_trade_history_for_pairs()
        sheet_handler.write_trades(trades)
        return trades
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return []

if __name__ == "__main__":
    main()