import gspread
import platform
import os
from oauth2client.service_account import ServiceAccountCredentials
import datetime
import logging
from google_sheet_config import google_sheet_config_instance
from services.trade_mapping_corrected import TradeHeaders, get_universal_headers

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
            worksheet = spreadsheet.add_worksheet(self.sheet_name, 1000, 26)
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

    def write_unified_trades(self, trades):
        """
        Writes unified trade data from multiple exchanges to the spreadsheet.
        
        Args:
            trades (list): List of trades in universal format
        """
        # Get the first row to check for headers
        first_row = self.sheet.row_values(1)
        headers = get_universal_headers()
        
        # Initialize headers only if the sheet is completely empty
        if not first_row:
            self.sheet.append_row(headers)
            logger.info("Universal headers written to the sheet.")
            
            # Format important columns
            self.sheet.format('C:D', {  # Trade ID and Order ID columns
                "numberFormat": {
                    "type": "TEXT"
                }
            })
        
        # Get all existing records to check for duplicates
        existing_records = self.sheet.get_all_records()
        
        # Create set of existing trade identifiers (Exchange + Trade ID)
        existing_trade_identifiers = set()
        for record in existing_records:
            if record.get('Exchange') and record.get('Trade ID'):
                identifier = f"{record['Exchange']}_{record['Trade ID']}"
                existing_trade_identifiers.add(identifier)

        new_trades_count = 0
        
        # Process each trade
        for trade in trades:
            try:
                # Create unique identifier
                trade_identifier = f"{trade.get('Exchange', '')}_{trade.get('Trade ID', '')}"
                
                if trade_identifier in existing_trade_identifiers:
                    logger.debug(f"Trade {trade_identifier} already exists. Skipping...")
                    continue

                # Prepare row data in the same order as headers
                row_data = []
                for header in headers:
                    value = trade.get(header, '')
                    row_data.append(str(value) if value is not None else '')
                
                self.sheet.append_row(row_data)
                existing_trade_identifiers.add(trade_identifier)
                new_trades_count += 1
                
                logger.debug(f"Trade written: {trade.get('Exchange')} - {trade.get('Symbol')} - {trade.get('Trade ID')}")
                
            except Exception as e:
                logger.error(f"Error writing trade to sheet: {e}")
                continue
        
        logger.info(f"Successfully wrote {new_trades_count} new trades to Google Sheets")

    def write_trades(self, trades):
        """
        Legacy method for backward compatibility.
        Maps old format trades and writes them.
        """
        logger.warning("Using legacy write_trades method. Consider using write_unified_trades instead.")
        
        # Convert old format to universal format if needed
        from services.trade_mapping_corrected import map_binance_trade
        
        mapped_trades = []
        for trade in trades:
            try:
                mapped_trade = map_binance_trade(trade)
                mapped_trades.append(mapped_trade)
            except Exception as e:
                logger.error(f"Error mapping legacy trade: {e}")
                continue
        
        # Use the new unified method
        self.write_unified_trades(mapped_trades)

    def clear_sheet(self):
        """Clears all data from the sheet."""
        self.sheet.clear()
        logger.info("Sheet cleared successfully")

    def get_trade_count(self):
        """
        Get the current number of trades in the sheet.
        
        Returns:
            int: Number of trades (excluding header row)
        """
        try:
            all_records = self.sheet.get_all_records()
            return len(all_records)
        except Exception as e:
            logger.error(f"Error getting trade count: {e}")
            return 0

    def backup_data(self, filename=None):
        """
        Create a backup of current sheet data.
        
        Args:
            filename (str): Optional filename for backup
            
        Returns:
            str: Backup filename
        """
        try:
            if not filename:
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"trade_backup_{timestamp}.json"
            
            all_records = self.sheet.get_all_records()
            
            import json
            with open(filename, 'w') as f:
                json.dump(all_records, f, indent=2, default=str)
            
            logger.info(f"Data backed up to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return None
