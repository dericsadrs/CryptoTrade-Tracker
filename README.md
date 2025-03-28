# Cryptocurrency Portfolio Tracker

A Python application that tracks cryptocurrency trades across multiple exchanges (Binance and Bybit) and automatically logs them to Google Sheets.

## Features

- Fetches trade history from Binance and Bybit exchanges
- Standardizes trade data formats across different exchanges
- Automatically logs trades to Google Sheets
- Avoids duplicate trade entries
- Supports tracking across multiple trading pairs

## Architecture

```
src/
├── app.py                     # Main application entry point
├── config.py                  # Configuration management
├── google_sheet_config.py     # Google Sheets configuration
├── services/
    ├── binance/
    │   └── binance_client.py  # Binance API client
    ├── bybit/
    │   └── bybit_client.py    # Bybit API client
    ├── googlesheet_handler.py # Google Sheets integration
    └── trade_mapping.py       # Trade data normalization
```

## Prerequisites

- Python 3.7+
- Google Cloud Platform account with Sheets API enabled
- Binance and/or Bybit account with API keys

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/CryptoCurrency-Portfolio-Tracker.git
   cd CryptoCurrency-Portfolio-Tracker
   ```

2. Set up your environment variables by creating a `.env` file in the project root:
   ```
   COINGECKO_API_KEY=your_coingecko_api_key
   BINANCE_API_KEY=your_binance_api_key
   BINANCE_SECRET_KEY=your_binance_secret_key
   BYBIT_API_KEY=your_bybit_api_key
   BYBIT_SECRET_KEY=your_bybit_secret_key
   ```

3. Create a `credentials` directory and add your Google Service Account credentials:
   ```bash
   mkdir -p credentials
   # Add your credentials.json file to the credentials directory
   ```

4. Install dependencies using the included Makefile:
   ```bash
   make install
   ```
   
   Or manually:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Configuration

### Google Sheets

1. Create a Service Account in the Google Cloud Platform console
2. Enable the Google Sheets API
3. Create a key for the service account and download as JSON
4. Place the JSON file in the `credentials` directory as `credentials.json`
5. Create a Google Sheet named "CryptoPortfolioTracker"
6. Share the sheet with the email address of your service account

### Exchange API Keys

1. Create API keys on Binance and/or Bybit with read-only permissions
2. Add these keys to your `.env` file

## Usage

Run the application using the Makefile:

```bash
make run
```

Or manually:

```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
python src/app.py
```

The application will:
1. Connect to your exchanges using the provided API keys
2. Fetch your recent trade history
3. Standardize the trade data across exchanges
4. Log the trades to the "trade_history" worksheet in your Google Sheet
5. Skip any duplicate trades that have already been recorded

## Makefile Commands

- `make`: Sets up venv, installs requirements, and runs the app
- `make venv`: Creates virtual environment if it doesn't exist
- `make install`: Installs requirements in virtual environment
- `make run`: Runs the application
- `make clean`: Removes virtual environment
- `make help`: Shows help message

## Trade Data Structure

Each trade entry contains the following standardized data:

- Exchange: The exchange where the trade occurred
- Symbol: The trading pair
- Trade ID: Unique identifier for the trade
- Price: The price at which the trade executed
- Quantity: The amount of cryptocurrency traded
- Total: The total value of the trade
- Side: Buy or Sell
- Time: Timestamp of the trade

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the project
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## Acknowledgments

- [Python-Binance](https://github.com/sammchardy/python-binance) for Binance API integration
- [PyBit](https://github.com/bybit-exchange/pybit) for Bybit API integration
- [GSpread](https://github.com/burnash/gspread) for Google Sheets integration
