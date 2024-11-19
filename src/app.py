from services.coingecko_api import CoinGeckoAPI
from services.googlesheet_handler import GoogleSheetHandler
from services.portfolio_updater import PortfolioUpdater


def main():
    # Path to credentials and spreadsheet name
    json_key_file = "credentials/credentials.json"
    sheet_name = "CryptoPortfolioTracker"

    # Initialize the handler
    handler = GoogleSheetHandler(json_key_file, sheet_name)

    # Example: Read and print the spreadsheet data
    portfolio_data = handler.read_portfolio()
    print("Current Portfolio:", portfolio_data)

    # Initialize CoinGecko API
    coingecko = CoinGeckoAPI()
    
    # Get prices for the cryptocurrencies in the portfolio
    crypto_names = ','.join([asset["Crypto"].split(' (')[0].strip().lower() for asset in portfolio_data if asset["Crypto"] != "Total "])
    prices = coingecko.get_price(crypto_names)
    print("Prices:", prices)

    # Update portfolio values and percentages
    updater = PortfolioUpdater(portfolio_data, prices)
    updated_portfolio = updater.update_portfolio()
    
    # Update the spreadsheet with the new portfolio data
    total_value = sum(item['Value (USD)'] for item in updated_portfolio if item['Value (USD)'])
    handler.update_portfolio(updated_portfolio, total_value=total_value)

    # Print updated portfolio
    print("Updated Portfolio:", updated_portfolio)


# Example usage
if __name__ == "__main__":
    # Replace with your actual API key
    coingecko = CoinGeckoAPI()
    
    # Check API status
    print("API Status:", coingecko.ping())
    
    # Run the main function to update the portfolio
    main()