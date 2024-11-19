import re

class PortfolioUpdater:
    def __init__(self, portfolio, prices):
        self.portfolio = portfolio
        self.prices = prices

    def update_portfolio(self):
        """Update the portfolio with current prices and calculate values and percentages."""
        total_value = 0
        for asset in self.portfolio:
            # Remove ticker symbol and get the crypto name
            crypto_name = re.sub(r'\s*\(.*?\)', '', asset["Crypto"]).strip().lower()
            quantity = asset["Quantity"]

            # Ensure quantity is treated as a number
            try:
                quantity = float(quantity) if quantity else 0
            except ValueError:
                quantity = 0  # Default to 0 if conversion fails

            # Get the price from the prices dictionary
            price = self.prices.get(crypto_name, {}).get('usd', 0)
            value = price * quantity

            # Update the asset details
            asset["Price (USD)"] = price
            asset["Value (USD)"] = value
            total_value += value

        # Update percentage of portfolio for each asset
        for asset in self.portfolio:
            if total_value > 0:
                asset["% of Portfolio"] = f"{(asset['Value (USD)'] / total_value) * 100:.2f}%"
            else:
                asset["% of Portfolio"] = "0%"

        return self.portfolio
