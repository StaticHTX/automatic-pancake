import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time

class CryptoAnalyzer:
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        
    def get_crypto_data(self, crypto_id="bitcoin", days=30):
        """
        Fetch historical price data for a cryptocurrency
        """
        endpoint = f"{self.base_url}/coins/{crypto_id}/market_chart"
        params = {
            "vs_currency": "usd",
            "days": days,
            "interval": "daily"
        }
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Convert price data to DataFrame
            df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
            df["date"] = pd.to_datetime(df["timestamp"], unit="ms")
            df = df.drop("timestamp", axis=1)
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None

    def calculate_metrics(self, df):
        """
        Calculate various metrics and indicators
        """
        if df is None or df.empty:
            return None
        
        # Calculate moving averages
        df["MA7"] = df["price"].rolling(window=7).mean()
        df["MA30"] = df["price"].rolling(window=30).mean()
        
        # Calculate daily returns
        df["daily_return"] = df["price"].pct_change()
        
        # Calculate volatility (30-day rolling standard deviation)
        df["volatility"] = df["daily_return"].rolling(window=30).std()
        
        return df

    def plot_analysis(self, df, crypto_id="bitcoin"):
        """
        Create visualization of the analysis
        """
        if df is None or df.empty:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Plot price and moving averages
        plt.plot(df["date"], df["price"], label="Price", color="blue")
        plt.plot(df["date"], df["MA7"], label="7-day MA", color="orange")
        plt.plot(df["date"], df["MA30"], label="30-day MA", color="red")
        
        plt.title(f"{crypto_id.capitalize()} Price Analysis")
        plt.xlabel("Date")
        plt.ylabel("Price (USD)")
        plt.legend()
        plt.grid(True)
        
        # Save the plot
        plt.savefig(f"{crypto_id}_analysis.png")
        plt.close()

def main():
    analyzer = CryptoAnalyzer()
    
    # List of cryptocurrencies to analyze
    cryptos = ["bitcoin", "ethereum", "cardano"]
    
    for crypto in cryptos:
        print(f"\nAnalyzing {crypto}...")
        
        # Get data
        df = analyzer.get_crypto_data(crypto)
        
        if df is not None:
            # Calculate metrics
            df_with_metrics = analyzer.calculate_metrics(df)
            
            # Create visualization
            analyzer.plot_analysis(df_with_metrics, crypto)
            
            # Print some basic statistics
            latest_price = df_with_metrics["price"].iloc[-1]
            avg_price = df_with_metrics["price"].mean()
            volatility = df_with_metrics["volatility"].iloc[-1]
            
            print(f"Latest Price: ${latest_price:.2f}")
            print(f"30-day Average Price: ${avg_price:.2f}")
            print(f"Current Volatility: {volatility:.4f}")
            print(f"Analysis saved as {crypto}_analysis.png")
        
        # Add delay to respect API rate limits
        time.sleep(1)

if __name__ == "__main__":
    main() 