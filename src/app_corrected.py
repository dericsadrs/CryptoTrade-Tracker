import json
import logging
from services.binance.binance_client_corrected import BinanceClient
from services.bybit.bybit_client_corrected import BybitClient
from services.googlesheet_handler import GoogleSheetHandler
from services.helpers import clean_asset_name
from google_sheet_config import Worksheet
from services.trade_mapping_corrected import map_binance_trade, map_bybit_trade

logger = logging.getLogger(__name__)

def get_binance_trades():
    """
    Efficiently fetches trades from Binance.
    
    Returns:
        list: List of all trades from Binance
    """
    client = BinanceClient()
    try:
        # Get account balances to determine relevant assets
        assets = client.get_account_balances()
        logger.info(f"Found {len(assets)} assets with balances")
        
        if not assets:
            logger.warning("No assets found in account")
            return []
        
        # Get symbols that involve user's assets
        symbols = client.get_symbols_for_assets(assets)
        logger.info(f"Found {len(symbols)} relevant trading symbols")
        
        if not symbols:
            logger.warning("No relevant trading symbols found")
            return []
        
        # Fetch trades for relevant symbols
        all_trades = client.get_recent_trades_batch(symbols, limit=500)
        logger.info(f"Retrieved {len(all_trades)} total Binance trades")
        
        return all_trades
        
    except Exception as e:
        logger.error(f"Error fetching Binance trades: {str(e)}")
        return []

def get_bybit_trades():
    """
    Fetches trades from Bybit using V5 API.
    
    Returns:
        list: List of all trades from Bybit
    """
    client = BybitClient()
    try:
        # Get all spot trading history
        all_trades = client.get_all_spot_trades(limit=100)
        logger.info(f"Retrieved {len(all_trades)} total Bybit trades")
        
        return all_trades
        
    except Exception as e:
        logger.error(f"Error fetching Bybit trades: {str(e)}")
        return []

def process_all_trades():
    """
    Process trades from both exchanges and return unified format.
    
    Returns:
        list: List of all trades in universal format
    """
    all_trades = []
    
    # Fetch and map Binance trades
    logger.info("Fetching Binance trades...")
    binance_trades = get_binance_trades()
    
    for trade in binance_trades:
        try:
            mapped_trade = map_binance_trade(trade)
            all_trades.append(mapped_trade)
        except Exception as e:
            logger.error(f"Error mapping Binance trade: {e}")
            continue
    
    # Fetch and map Bybit trades
    logger.info("Fetching Bybit trades...")
    bybit_trades = get_bybit_trades()
    
    for trade in bybit_trades:
        try:
            mapped_trade = map_bybit_trade(trade)
            all_trades.append(mapped_trade)
        except Exception as e:
            logger.error(f"Error mapping Bybit trade: {e}")
            continue
    
    # Sort all trades by time (newest first)
    all_trades.sort(
        key=lambda x: x.get('Time', ''), 
        reverse=True
    )
    
    logger.info(f"Total trades processed: {len(all_trades)}")
    return all_trades

def main():
    """
    Main function to fetch trades from both exchanges and write to Google Sheets.
    """
    try:
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Initialize Google Sheets handler
        sheet_handler = GoogleSheetHandler(Worksheet.TRADE_HISTORY)
        
        # Process all trades from both exchanges
        all_trades = process_all_trades()
        
        if not all_trades:
            logger.warning("No trades found from any exchange")
            return []
        
        # Write to Google Sheets
        logger.info("Writing trades to Google Sheets...")
        sheet_handler.write_unified_trades(all_trades)
        
        logger.info("Trade processing completed successfully")
        return all_trades
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        return []

if __name__ == "__main__":
    main()
