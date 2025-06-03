#!/usr/bin/env python3
"""
Setup and Testing Script for CryptoCurrency Portfolio Tracker
Validates API connections and basic functionality
"""

import os
import sys
import logging
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config import config_instance
from services.binance.binance_client_corrected import BinanceClient
from services.bybit.bybit_client_corrected import BybitClient

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('setup_test.log'),
            logging.StreamHandler()
        ]
    )

def check_environment():
    """Check if required environment variables are set"""
    logger = logging.getLogger(__name__)
    
    required_vars = [
        'BINANCE_API_KEY',
        'BINANCE_SECRET_KEY',
        'BYBIT_API_KEY', 
        'BYBIT_SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing environment variables: {missing_vars}")
        logger.error("Please set these in your .env file")
        return False
    
    logger.info("✓ All required environment variables are set")
    return True

def test_binance_connection():
    """Test Binance API connection"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Testing Binance connection...")
        client = BinanceClient()
        
        # Test account access
        balances = client.get_account_balances()
        logger.info(f"✓ Binance connection successful. Found {len(balances)} assets with balances")
        
        # Test getting trading symbols
        if balances:
            symbols = client.get_symbols_for_assets(balances[:5])  # Test with first 5 assets
            logger.info(f"✓ Found {len(symbols)} relevant trading symbols")
            
            # Test getting trade history for one symbol if available
            if symbols:
                test_symbol = symbols[0]
                trades = client.get_trade_history(test_symbol, limit=10)
                logger.info(f"✓ Retrieved {len(trades)} recent trades for {test_symbol}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Binance connection failed: {e}")
        return False

def test_bybit_connection():
    """Test Bybit API connection"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Testing Bybit connection...")
        client = BybitClient()
        
        # Test account access
        balance = client.get_account_balance()
        logger.info("✓ Bybit connection successful")
        
        # Test getting instruments
        instruments = client.get_instruments_info()
        logger.info(f"✓ Found {len(instruments)} available instruments")
        
        # Test getting execution history
        executions = client.get_execution_history(limit=10)
        logger.info(f"✓ Retrieved {len(executions)} recent executions")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Bybit connection failed: {e}")
        return False

def test_data_mapping():
    """Test trade data mapping functionality"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Testing data mapping...")
        
        from services.trade_mapping_corrected import map_binance_trade, map_bybit_trade, get_universal_headers
        
        # Test Binance mapping with sample data
        sample_binance_trade = {
            'symbol': 'BTCUSDT',
            'id': 12345,
            'orderId': 67890,
            'price': '50000.00',
            'qty': '0.001',
            'commission': '0.05',
            'commissionAsset': 'USDT',
            'time': 1640995200000,  # 2022-01-01 00:00:00
            'isBuyer': True,
            'isMaker': False
        }
        
        mapped_binance = map_binance_trade(sample_binance_trade)
        logger.info("✓ Binance trade mapping successful")
        
        # Test Bybit mapping with sample data
        sample_bybit_trade = {
            'symbol': 'BTCUSDT',
            'execId': 'abc123',
            'orderId': 'def456',
            'execPrice': '50000.00',
            'execQty': '0.001',
            'execValue': '50.00',
            'execFee': '0.05',
            'feeCurrency': 'USDT',
            'execTime': '1640995200000',
            'side': 'Buy',
            'isMaker': False
        }
        
        mapped_bybit = map_bybit_trade(sample_bybit_trade)
        logger.info("✓ Bybit trade mapping successful")
        
        # Test headers
        headers = get_universal_headers()
        logger.info(f"✓ Universal headers: {len(headers)} columns")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Data mapping test failed: {e}")
        return False

def run_quick_integration_test():
    """Run a quick integration test"""
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("Running integration test...")
        
        from app_corrected import process_all_trades
        
        # This will fetch a small amount of data from both exchanges
        trades = process_all_trades()
        
        if trades:
            logger.info(f"✓ Integration test successful. Processed {len(trades)} trades")
            
            # Show sample of different exchanges
            exchanges = set(trade.get('Exchange', 'Unknown') for trade in trades)
            logger.info(f"✓ Data from exchanges: {', '.join(exchanges)}")
            
        else:
            logger.warning("⚠ Integration test completed but no trades found")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Integration test failed: {e}")
        return False

def check_dependencies():
    """Check if all required packages are installed"""
    logger = logging.getLogger(__name__)
    
    required_packages = [
        'gspread',
        'oauth2client', 
        'python-dotenv',
        'binance',
        'pybit',
        'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing packages: {missing_packages}")
        logger.error("Run: pip install -r requirements_corrected.txt")
        return False
    
    logger.info("✓ All required packages are installed")
    return True

def main():
    """Main testing function"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("CryptoCurrency Portfolio Tracker - Setup Test")
    logger.info("=" * 50)
    
    tests = [
        ("Dependencies", check_dependencies),
        ("Environment", check_environment),
        ("Binance API", test_binance_connection),
        ("Bybit API", test_bybit_connection),
        ("Data Mapping", test_data_mapping),
        ("Integration", run_quick_integration_test)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results[test_name] = False
    
    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("TEST SUMMARY")
    logger.info("=" * 50)
    
    passed = 0
    total = len(tests)
    
    for test_name, passed_test in results.items():
        status = "✓ PASS" if passed_test else "✗ FAIL"
        logger.info(f"{test_name:<15}: {status}")
        if passed_test:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Your setup is ready.")
    else:
        logger.warning(f"⚠ {total - passed} test(s) failed. Please fix issues before proceeding.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
