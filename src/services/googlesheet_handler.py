import gspread
import platform
import os
from oauth2client.service_account import ServiceAccountCredentials


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
