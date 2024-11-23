import gspread
import platform
import os
from oauth2client.service_account import ServiceAccountCredentials
import datetime  # Import datetime for time conversion
import logging
from google_sheet_config import google_sheet_config_instance

logger = logging.getLogger(__name__)

class GoogleSheetHandler:
    def __init__(self, sheet_name):
        self.json_key_file = google_sheet_config_instance.get_credentials_path()
        self.spreadsheet_name = google_sheet_config_instance.get_sheet_name()
        self.sheet_name = sheet_name
        self.sheet = self.authenticate_and_open_sheet()

    def authenticate_and_open_sheet(self):
        """Authenticates and opens the specified Google Sheet."""
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(self.json_key_file, scope)
        client = gspread.authorize(credentials)
        
        # Open the spreadsheet
        spreadsheet = client.open(self.spreadsheet_name)
        
        try:
            # Try to open existing sheet
            worksheet = spreadsheet.worksheet(self.sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            # If sheet doesn't exist, create it
            worksheet = spreadsheet.add_worksheet(self.sheet_name, 1000, 26)  # Default rows and columns
            logger.info(f"Created new worksheet: {self.sheet_name}")
            
        return worksheet

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
        
        # Convert existing trade IDs to integers for comparison
        existing_trade_ids = {int(float(record['Trade ID'])) for record in existing_records if record['Trade ID']}  # Handle any format

        # Prepare headers
        headers = ["Symbol", "Trade ID", "Order ID", "Price", "Quantity", "Quote Quantity", "Commission", "Commission Asset", "Time"]

        # Check if sheet is empty and write headers if necessary
        if not existing_records:
            self.sheet.append_row(headers)
            
            # Format the Trade ID and Order ID columns as plain text
            self.sheet.format('B:C', {
                "numberFormat": {
                    "type": "TEXT"
                }
            })

        # Iterate over the trades and write new ones
        for trade in trades:
            trade_id = int(trade.get('id', 0))  # Convert to integer for comparison
            
            if trade_id in existing_trade_ids:
                logger.info(f"Trade ID {trade_id} already exists. Skipping...")
                continue

            # Convert timestamp
            timestamp_ms = trade.get('time', 0)
            timestamp_s = timestamp_ms / 1000.0
            readable_time = datetime.datetime.fromtimestamp(timestamp_s).strftime('%Y-%m-%d %H:%M:%S')

            self.sheet.append_row([
                trade.get('symbol', ''),
                str(trade_id),  # Store as string to prevent decimal formatting
                str(trade.get('orderId', '')),
                trade.get('price', ''),
                trade.get('qty', ''),
                trade.get('quoteQty', ''),
                trade.get('commission', ''),
                trade.get('commissionAsset', ''),
                readable_time,
            ])