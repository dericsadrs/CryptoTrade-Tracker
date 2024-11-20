import gspread
import platform
import os
from oauth2client.service_account import ServiceAccountCredentials
import datetime  # Import datetime for time conversion
import logging

logger = logging.getLogger(__name__)


class GoogleSheetHandler:
    def __init__(self, json_key_file, sheet_name):
        self.json_key_file = json_key_file
        self.sheet = self.authenticate_and_open_sheet(sheet_name)

    def authenticate_and_open_sheet(self, sheet_name):
        """Authenticates and opens the Google Sheet."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_key_file, scope)
        client = gspread.authorize(credentials)
        return client.open(sheet_name).sheet1

    def read_portfolio(self):
        """Reads portfolio data from the spreadsheet."""
        return self.sheet.get_all_records()

    def update_portfolio(self, portfolio, total_value):
        """Updates the spreadsheet with the portfolio data."""
        self.sheet.clear()
        headers = ["Crypto", "Quantity", "Price (USD)", "Value (USD)", "% of Portfolio"]
        self.sheet.append_row(headers)

        for asset in portfolio:
            self.sheet.append_row([
                asset["Crypto"],
                asset["Quantity"],
                asset.get("Price (USD)", 0),
                asset.get("Value (USD)", 0),
                asset.get("% of Portfolio", "0%")
            ])

    def write_trades(self, trades):
        """Writes trade data to the spreadsheet, skipping existing Trade IDs."""
        # Read existing records to check for existing Trade IDs
        existing_records = self.sheet.get_all_records()
        existing_trade_ids = {record['Trade ID'] for record in existing_records if 'Trade ID' in record}  # Create a set of existing Trade IDs

        # Prepare headers
        headers = ["Symbol", "Trade ID", "Order ID", "Price", "Quantity", "Quote Quantity", "Commission", "Commission Asset", "Time", "Is Buyer", "Is Maker", "Is Best Match"]

        # Check if the sheet is empty and write headers if necessary
        if not existing_records:
            self.sheet.append_row(headers)  # Write headers if the sheet is empty
        else:
            # Ensure headers are present
            current_headers = existing_records[0].keys()
            if set(headers) != set(current_headers):
                logger.warning("Headers do not match. Please check the spreadsheet format.")
                return

        # Iterate over the trades and write new ones
        for trade in trades:
            trade_id = trade.get('id', '')
            if trade_id in existing_trade_ids:
                logger.info(f"Trade ID {trade_id} already exists. Skipping...")
                continue  # Skip this trade if it already exists

            # Convert the timestamp from milliseconds to a readable format
            timestamp_ms = trade.get('time', 0)
            timestamp_s = timestamp_ms / 1000.0  # Convert to seconds
            readable_time = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')

            # Append the new trade to the sheet
            self.sheet.append_row([
                trade.get('symbol', ''),
                trade_id,  # Use the Trade ID
                trade.get('orderId', ''),
                trade.get('price', ''),
                trade.get('qty', ''),
                trade.get('quoteQty', ''),
                trade.get('commission', ''),
                trade.get('commissionAsset', ''),
                readable_time,  # Use the converted readable time
                trade.get('isBuyer', ''),
                trade.get('isMaker', ''),
                trade.get('isBestMatch', '')
            ])
