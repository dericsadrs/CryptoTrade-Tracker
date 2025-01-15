from google_sheet_config import Worksheet
from services.binance.binance_client import BinanceClient
from services.bybit.bybit_client import BybitClient
from services.googlesheet_handler import GoogleSheetHandler
from services.trade_mapping import map_binance_trade, map_bybit_trade
import logging

logger = logging.getLogger(__name__)

def get_binance_trades():
    """
    Fetches and maps all trades from Binance
    
    Returns:
        list: List of mapped Binance trades
    """
    client = BinanceClient()
    try:
        account = client.client.get_account()
        assets = [b['asset'] for b in account['balances'] 
                 if float(b['free']) > 0.00001 or float(b['locked']) > 0.00001]
        
        all_trades = []
        for asset in assets:
            trades = client.get_trade_history(asset)
            mapped_trades = [map_binance_trade(trade) for trade in trades]
            all_trades.extend(mapped_trades)
        
        return all_trades
    except Exception as e:
        logger.error(f"Error fetching Binance trades: {str(e)}")
        return []

def get_bybit_trades():
    """
    Fetches and maps all trades from Bybit
    
    Returns:
        list: List of mapped Bybit trades
    """
    client = BybitClient()
    try:
        trades = client.get_trade_history()
        mapped_trades = [map_bybit_trade(trade) for trade in trades]
        return mapped_trades
    except Exception as e:
        logger.error(f"Error fetching Bybit trades: {str(e)}")
        return []

def main():
    try:
        # Get trades from both exchanges
        binance_trades = get_binance_trades()
        bybit_trades = get_bybit_trades()
        
        # Combine all trades
        all_trades = binance_trades + bybit_trades
        
        # Write to Google Sheets
        if all_trades:
            sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
            sheet_handler.write_trades(all_trades)
            
        return all_trades
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return []

if __name__ == "__main__":
    trades = main()
    print(f"Retrieved {len(trades)} total trades")
    print(f"- Binance trades: {len([t for t in trades if t['Exchange'] == 'Binance'])}")
    print(f"- Bybit trades: {len([t for t in trades if t['Exchange'] == 'Bybit'])}")