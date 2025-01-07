# trade_mapping.py

from enum import Enum
from typing import Dict, Any, List
import datetime

class TradeHeaders(str, Enum):
    """Essential trade headers common across exchanges"""
    EXCHANGE = 'Exchange'
    SYMBOL = 'Symbol'
    TRADE_ID = 'Trade ID'
    PRICE = 'Price'
    QUANTITY = 'Quantity'
    TOTAL = 'Total'  # Price * Quantity
    SIDE = 'Side'    # Buy/Sell
    TIME = 'Time'

# Define a constant for milliseconds to seconds conversion
MILLISECONDS_TO_SECONDS = 1000.0

def map_binance_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps Binance trade response to simplified universal format
    
    Args:
        trade: Raw trade data from Binance API
        
    Returns:
        Dict with standardized trade data
    """
    # Convert timestamp to readable format
    timestamp_ms = trade.get('time', 0)
    timestamp_s = timestamp_ms / MILLISECONDS_TO_SECONDS
    readable_time = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    
    # Determine trade side
    side = 'BUY' if trade.get('isBuyer', False) else 'SELL'
    
    # Error handling for price and quantity
    try:
        price = float(trade.get('price', 0))
        quantity = float(trade.get('qty', 0))
    except (ValueError, TypeError):
        price = 0.0
        quantity = 0.0
    
    # Calculate total value
    total = price * quantity
    
    return {
        TradeHeaders.EXCHANGE: 'Binance',
        TradeHeaders.SYMBOL: trade.get('symbol', ''),
        TradeHeaders.TRADE_ID: str(trade.get('id', '')),
        TradeHeaders.PRICE: str(price),
        TradeHeaders.QUANTITY: str(quantity),
        TradeHeaders.TOTAL: str(total),
        TradeHeaders.SIDE: side,
        TradeHeaders.TIME: readable_time
    }

def get_universal_headers() -> List[str]:
    """Returns list of universal trade headers"""
    return [header.value for header in TradeHeaders]