
from services.coingecko_api import CoinGeckoAPI
from services.googlesheet_handler import GoogleSheetHandler


def main():
    # Path to credentials and spreadsheet name
    json_key_file = "credentials/credentials.json"
    sheet_name = "CryptoPortfolioTracker"

    # Initialize the handler
    handler = GoogleSheetHandler(json_key_file, sheet_name)

    # Example: Read and print the spreadsheet data
    portfolio_data = handler.read_portfolio()
    print("Current Portfolio:", portfolio_data)

    # # Example: Update the portfolio with sample data
    # sample_portfolio = [
    #     {"crypto": "Bitcoin", "quantity": 0.5, "price": 50000, "value": 25000, "percentage": 50.0},
    #     {"crypto": "Ethereum", "quantity": 2, "price": 2000, "value": 4000, "percentage": 8.0},
    # ]
    # handler.update_portfolio(sample_portfolio, total_value=50000)

# Example usage
if __name__ == "__main__":
    
    # Replace with your actual API key
    coingecko = CoinGeckoAPI()
    
    # Check API status
    print("API Status:", coingecko.ping())
    
    # Get price of Bitcoin and Ethereum
    print("Prices:", coingecko.get_price("bitcoin,ethereum"))
    
    # Get list of all supported coins
    print("Coins List:", coingecko.get_coins_list()[:5])  # Print first 5 coins for brevity
    
    # Get detailed data for Bitcoin
    print("Bitcoin Data:", coingecko.get_coin_data("bitcoin"))
    
    # Get market data for Bitcoin
    print("Bitcoin Market Data:", coingecko.get_market_data("bitcoin"))