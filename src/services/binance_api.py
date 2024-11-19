import time
import hmac
import hashlib
import requests
import logging
from urllib.parse import urlencode
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_asset_name(asset):
    """Remove LD prefix and handle special cases"""
    if asset.startswith('LD'):
        return asset[2:]  # Remove 'LD' prefix
    return asset

def get_all_trades(api_key, api_secret):
    try:
        base_url = 'https://api.binance.com'
        
        logger.info("Starting trade fetch process...")
        
        # Get account information
        endpoint = '/api/v3/account'
        timestamp = int(time.time() * 1000)
        
        params = {
            'timestamp': timestamp
        }
        
        query_string = urlencode(params)
        signature = hmac.new(
            api_secret.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        params['signature'] = signature
        headers = {
            'X-MBX-APIKEY': api_key
        }
        
        logger.info("Fetching account information...")
        
        response = requests.get(
            f"{base_url}{endpoint}",
            params=params,
            headers=headers
        )
        
        if response.status_code != 200:
            logger.error(f"Error getting account info. Status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return []
            
        account_data = response.json()
        
        # Clean up asset names by removing LD prefix
        balances = account_data['balances']
        assets = [clean_asset_name(b['asset']) for b in balances if float(b['free']) > 0 or float(b['locked']) > 0]
        
        logger.info(f"Found assets (after cleaning): {', '.join(assets)}")
        
        # Common trading pairs format
        trading_pairs = []
        for asset in assets:
            if asset != 'USDT':  # USDT is usually the quote asset
                trading_pairs.append(f"{asset}USDT")  # Most common format
            # if asset != 'BNB':
            #     trading_pairs.append(f"{asset}BNB")   # Some pairs trade against BNB
        
        logger.info(f"Checking trading pairs: {', '.join(trading_pairs)}")
        
        all_trades = []
        for pair in trading_pairs:
            logger.info(f"Fetching trades for {pair}...")
            
            try:
                timestamp = int(time.time() * 1000)
                params = {
                    'symbol': pair,
                    'timestamp': timestamp,
                    'limit': 1000
                }
                
                query_string = urlencode(params)
                signature = hmac.new(
                    api_secret.encode('utf-8'),
                    query_string.encode('utf-8'),
                    hashlib.sha256
                ).hexdigest()
                params['signature'] = signature
                
                trades_response = requests.get(
                    f"{base_url}/api/v3/myTrades",
                    params=params,
                    headers=headers
                )
                
                if trades_response.status_code == 200:
                    symbol_trades = trades_response.json()
                    if symbol_trades:
                        logger.info(f"Found {len(symbol_trades)} trades for {pair}")
                        all_trades.extend(symbol_trades)
                else:
                    logger.warning(f"Failed to get trades for {pair}. Status code: {trades_response.status_code}")
                    logger.warning(f"Response: {trades_response.text}")
                    
            except Exception as e:
                logger.error(f"Error processing {pair}: {str(e)}")
                continue
                
            time.sleep(0.1)  # Rate limiting
        
        logger.info(f"Total trades found: {len(all_trades)}")
        return all_trades

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return []
