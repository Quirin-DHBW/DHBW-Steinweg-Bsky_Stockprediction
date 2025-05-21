import yfinance as yf
import pandas as pd
from datetime import *

SINCE = datetime(year=2025, month=1, day=1)
UNTIL = datetime(year=2025, month=1, day=31)
STOCK = "TSLA"
SEARCH_TERMS = ["Tesla", "Elon", "Musk", "electric", "car"]
POSTS_PER_DAY = 100

single_day = timedelta(days=1)
n_days_timeframe = ((UNTIL - SINCE) // single_day) + 1

days = []
for i in range(n_days_timeframe):
    today_dt = SINCE + (i * single_day)
    tomorrow_dt = SINCE + ((i + 1) * single_day)
    today = today_dt.strftime("%Y-%m-%d")
    tomorrow = tomorrow_dt.strftime("%Y-%m-%d")
    days.append((today, tomorrow))


def fetch_stock_data(ticker, start_date, end_date):
    print(f"Lade Daten für {ticker}...")

    # Fetch raw stock data
    df = yf.download(ticker, start=start_date, end=end_date)
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()

    # Create a date range that includes all days (even weekends)
    full_index = pd.date_range(start=start_date, end=end_date, freq='D')

    # Reindex the DataFrame to include all days
    df_full = df.reindex(full_index)

    # Fill missing values
    df_full.interpolate(method='linear', inplace=True)
    df_full.ffill(inplace=True)
    df_full.bfill(inplace=True)

    df_full.reset_index(inplace=True)
    df_full.rename(columns={'index': 'Date'}, inplace=True)

    print("Download abgeschlossen.")
    return df_full

# Fetch and print data
data = fetch_stock_data(STOCK, start_date="2025-01-01", end_date="2025-01-31")
print(data.head(40))
