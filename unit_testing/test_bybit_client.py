import unittest
from unittest.mock import patch, MagicMock
from services.bybit.bybit_client import BybitClient

class TestBybitClient(unittest.TestCase):
    @patch('services.bybit_client.HTTP')
    def test_get_account(self, mock_bybit_client):
        # Mock Bybit API response
        mock_client_instance = MagicMock()
        mock_client_instance.get_wallet_balance.return_value = {
            'result': {
                'BTC': {'equity': '0.5', 'available_balance': '0.4'},
                'ETH': {'equity': '1.2', 'available_balance': '1.0'}
            }
        }
        mock_bybit_client.return_value = mock_client_instance

        client = BybitClient()
        balance = client.client.get_wallet_balance()

        self.assertIn('BTC', balance['result'])
        self.assertEqual(balance['result']['BTC']['equity'], '0.5')

    @patch('services.bybit_client.HTTP')
    def test_get_trade_history(self, mock_bybit_client):
        # Mock Bybit trade history response
        mock_client_instance = MagicMock()
        mock_client_instance.get_trade_records.return_value = {
            'result': [
                {'symbol': 'BTCUSDT', 'order_id': '123', 'price': '45000', 'qty': '0.1', 'side': 'Buy', 'time': '1617187200'},
                {'symbol': 'ETHUSDT', 'order_id': '124', 'price': '3000', 'qty': '1', 'side': 'Sell', 'time': '1617190800'}
            ]
        }
        mock_bybit_client.return_value = mock_client_instance

        client = BybitClient()
        trades = client.get_trade_history('BTCUSDT')

        self.assertEqual(len(trades), 2)
        self.assertEqual(trades[0]['symbol'], 'BTCUSDT')
        self.assertEqual(trades[0]['price'], '45000')