import unittest
from unittest.mock import patch, MagicMock
from services.binance.binance_client import BinanceClient

class TestBinanceClient(unittest.TestCase):

    @patch('services.binance_client.Client')
    def test_get_account(self, mock_binance_client):
        # Mock Binance API response
        mock_client_instance = MagicMock()
        mock_client_instance.get_account.return_value = {
            'balances': [
                {'asset': 'BTC', 'free': '0.5', 'locked': '0.1'},
                {'asset': 'ETH', 'free': '1.2', 'locked': '0.0'}
            ]
        }
        mock_binance_client.return_value = mock_client_instance

        client = BinanceClient()
        account = client.client.get_account()

        self.assertEqual(len(account['balances']), 2)
        self.assertEqual(account['balances'][0]['asset'], 'BTC')
        self.assertEqual(account['balances'][0]['free'], '0.5')

    @patch('services.binance_client.Client')
    def test_get_trade_history(self, mock_binance_client):
        # Mock Binance trade history response
        mock_client_instance = MagicMock()
        mock_client_instance.get_my_trades.return_value = [
            {'symbol': 'BTCUSDT', 'id': 1, 'price': '50000', 'qty': '0.1', 'isBuyer': True, 'time': 1617187200000},
            {'symbol': 'ETHUSDT', 'id': 2, 'price': '4000', 'qty': '1', 'isBuyer': False, 'time': 1617190800000}
        ]
        mock_binance_client.return_value = mock_client_instance

        client = BinanceClient()
        trades = client.get_trade_history('BTCUSDT')

        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]['symbol'], 'BTCUSDT')
        self.assertEqual(trades[0]['price'], '50000')