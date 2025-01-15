import logging
from services.binance.binance_client import BinanceClient
from services.bybit.bybit_client import BybitClient
from services.googlesheet_handler import GoogleSheetHandler
from google_sheet_config import Worksheet

logger = logging.getLogger(__name__)

def fetch_binance_trades():
    """
    Fetches all trades from Binance for available trading pairs.

    Returns:
        list: List of all trades from Binance.
    """
    client = BinanceClient()
    try:
        account = client.client.get_account()
        assets = [b['asset'] for b in account['balances'] if float(b['free']) > 0 or float(b['locked']) > 0]
        available_pairs = client.fetch_trading_pairs(assets)
        logger.info(f"Available trading pairs: {available_pairs}")

        return [trade for pair in available_pairs for trade in client.get_trade_history(pair)]
    except Exception as e:
        logger.error(f"Error fetching Binance trades: {str(e)}")
        return []

def fetch_bybit_trades():
    """
    Fetches all trades from Bybit.

    Returns:
        list: List of all trades from Bybit.
    """
    client = BybitClient()
    try:
        return client.get_trade_history()
    except Exception as e:
        logger.error(f"Error fetching Bybit trades: {str(e)}")
        return []

def main():
    """Main entry point for the application."""
    try:
        sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
        binance_trades = fetch_binance_trades()
        bybit_trades = fetch_bybit_trades()
        all_trades = binance_trades + bybit_trades

        if all_trades:
            sheet_handler.write_trades(all_trades)
            logger.info(f"{len(all_trades)} trades successfully written to the sheet.")
        else:
            logger.warning("No trades fetched to write to the sheet.")
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")

if __name__ == "__main__":
    main()
