from enum import Enum
from typing import Dict, Any
import datetime

class TradeHeaders(str, Enum):
    """Universal trade headers for all exchanges"""
    EXCHANGE = 'Exchange'
    SYMBOL = 'Symbol'
    TRADE_ID = 'Trade ID'
    ORDER_ID = 'Order ID'
    PRICE = 'Price'
    QUANTITY = 'Quantity'
    TOTAL = 'Total'
    SIDE = 'Side'
    TIME = 'Time'
    FEE = 'Fee'
    FEE_ASSET = 'Fee Asset'
    IS_MAKER = 'Is Maker'

def map_binance_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps Binance trade response to universal format.
    Based on official /api/v3/myTrades response structure.
    
    Args:
        trade: Raw trade data from Binance API
        
    Returns:
        Dict with standardized trade data
    """
    # Convert timestamp to readable format
    timestamp_ms = trade.get('time', 0)
    timestamp_s = timestamp_ms / 1000.0
    readable_time = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    
    # Determine trade side
    side = 'BUY' if trade.get('isBuyer', False) else 'SELL'
    
    # Calculate values
    price = float(trade.get('price', 0))
    quantity = float(trade.get('qty', 0))
    total = price * quantity
    
    return {
        TradeHeaders.EXCHANGE: 'Binance',
        TradeHeaders.SYMBOL: trade.get('symbol', ''),
        TradeHeaders.TRADE_ID: str(trade.get('id', '')),
        TradeHeaders.ORDER_ID: str(trade.get('orderId', '')),
        TradeHeaders.PRICE: str(price),
        TradeHeaders.QUANTITY: str(quantity),
        TradeHeaders.TOTAL: str(total),
        TradeHeaders.SIDE: side,
        TradeHeaders.TIME: readable_time,
        TradeHeaders.FEE: str(trade.get('commission', '0')),
        TradeHeaders.FEE_ASSET: trade.get('commissionAsset', ''),
        TradeHeaders.IS_MAKER: str(trade.get('isMaker', False))
    }

def map_bybit_trade(trade: Dict[str, Any]) -> Dict[str, Any]:
    """
    Maps Bybit V5 execution response to universal format.
    Based on official /v5/execution/list response structure.
    
    Args:
        trade: Raw trade data from Bybit V5 API
        
    Returns:
        Dict with standardized trade data
    """
    # Convert timestamp to readable format
    timestamp_ms = int(trade.get('execTime', 0))
    timestamp_s = timestamp_ms / 1000.0
    readable_time = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')
    
    # Calculate values
    price = float(trade.get('execPrice', 0))
    quantity = float(trade.get('execQty', 0))
    total = float(trade.get('execValue', 0))
    
    return {
        TradeHeaders.EXCHANGE: 'Bybit',
        TradeHeaders.SYMBOL: trade.get('symbol', ''),
        TradeHeaders.TRADE_ID: trade.get('execId', ''),
        TradeHeaders.ORDER_ID: trade.get('orderId', ''),
        TradeHeaders.PRICE: str(price),
        TradeHeaders.QUANTITY: str(quantity),
        TradeHeaders.TOTAL: str(total),
        TradeHeaders.SIDE: trade.get('side', ''),
        TradeHeaders.TIME: readable_time,
        TradeHeaders.FEE: str(trade.get('execFee', '0')),
        TradeHeaders.FEE_ASSET: trade.get('feeCurrency', ''),
        TradeHeaders.IS_MAKER: str(trade.get('isMaker', False))
    }

def get_universal_headers() -> list:
    """Returns list of universal trade headers"""
    return [header.value for header in TradeHeaders]
