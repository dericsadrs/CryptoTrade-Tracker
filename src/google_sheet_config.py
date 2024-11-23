from enum import Enum

class Worksheet(str, Enum):
    """Enum for worksheet names"""
    TRADE_HISTORY = 'trade_history'
  

class GoogleSheetsConfig:
    """Configuration for Google Sheets integration"""
    
    #for local testing, generate a key for the IAM account that you've given permission
    CREDENTIALS_PATH = 'credentials/credentials.json'
    SHEET_NAME = 'CryptoPortfolioTracker'
    
    @classmethod
    def get_credentials_path(cls):
        """Get credentials path"""
        return cls.CREDENTIALS_PATH
    
    @classmethod
    def get_sheet_name(cls):
        """Get sheet name"""
        return cls.SHEET_NAME
    
    @classmethod
    def get_worksheet_name(cls, worksheet: Worksheet):
        """Get worksheet name"""
        return worksheet.value
    
# global instance
google_sheet_config_instance = GoogleSheetsConfig()