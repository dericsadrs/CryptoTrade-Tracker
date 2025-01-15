import gspread
import platform
import os
from oauth2client.service_account import ServiceAccountCredentials
import datetime  # Import datetime for time conversion
import logging
from google_sheet_config import google_sheet_config_instance
from services.trade_mapping import TradeHeaders, get_universal_headers, map_binance_trade, map_bybit_trade

logger = logging.getLogger(__name__)

class GoogleSheetHandler:
    # Constants for default worksheet size
    DEFAULT_ROWS = 1000
    DEFAULT_COLUMNS = 26

    def __init__(self, sheet_name: str):
        """Initializes the GoogleSheetHandler with the specified sheet name."""
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
            worksheet = spreadsheet.add_worksheet(self.sheet_name, self.DEFAULT_ROWS, self.DEFAULT_COLUMNS)
            logger.info(f"Created new worksheet: {self.sheet_name}")
            
        return worksheet

    def read_portfolio(self) -> list:
        """Reads portfolio data from the spreadsheet."""
        return self.sheet.get_all_records()

    def update_portfolio(self, portfolio: list, total_value: float):
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

    
    def write_trades(self, trades: list):
        """Writes simplified trade data to the spreadsheet"""
        # Get the first row to check for headers
        first_row = self.sheet.row_values(1)
        headers = get_universal_headers()
        
        # Initialize headers only if the sheet is completely empty
        if not first_row:
            self.sheet.append_row(headers)
            logger.info("Headers written to the sheet.")
            
            # Format the Trade ID column as plain text
            self.sheet.format('C', {
                "numberFormat": {
                    "type": "TEXT"
                }
            })
        
        # Get all records (excluding the header row) to check for existing Trade IDs
        existing_records = self.sheet.get_all_records()
        # Store Trade IDs as strings to handle both numeric and string IDs
        existing_trade_ids = {str(record['Trade ID']).strip() for record in existing_records if record['Trade ID']}
        logger.info(f"Found {len(existing_trade_ids)} existing trade IDs")

        new_trades_count = 0
        skipped_trades_count = 0

        # Iterate over the trades and write new ones
        for trade in trades:
            # Determine if it's a Bybit trade by checking for Bybit-specific fields
            is_bybit = 'createdTime' in trade and 'orderId' in trade
            
            # Map the trade data using the appropriate mapping function
            mapped_trade = map_bybit_trade(trade) if is_bybit else map_binance_trade(trade)
            
            trade_id = str(mapped_trade[TradeHeaders.TRADE_ID]).strip()
            if trade_id in existing_trade_ids:
                logger.debug(f"Trade ID {trade_id} already exists. Skipping...")
                skipped_trades_count += 1
                continue
            
            # Prepare row data in the same order as headers
            row_data = [mapped_trade[header] for header in TradeHeaders]
            
            self.sheet.append_row(row_data)
            new_trades_count += 1
            logger.debug(f"Trade data written: {row_data}")

        logger.info(f"Processed trades summary: {new_trades_count} new trades written, {skipped_trades_count} duplicates skipped")