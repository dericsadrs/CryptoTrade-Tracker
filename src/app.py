
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

if __name__ == "__main__":
    main()