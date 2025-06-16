import sys, os
os.chdir(os.path.dirname(sys.argv[0]))

import pandas as pd
from prophet import Prophet
import duckdb
import matplotlib.pyplot as plt
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

FILE_HEAD = "tsla_20240101_20250430"
POSTS = FILE_HEAD + "_posts.db"
STOCK = FILE_HEAD + "_stock.db"

N_DAYS_TO_PREDICT = 60

con = duckdb.connect(STOCK)
df_stock = con.execute("SELECT * FROM stock_values").fetchdf()
con.close()

con = duckdb.connect(POSTS)
df_posts = con.execute("SELECT timestamp, text FROM posts").fetchdf()
con.close()

# Replace stock column names for clarity
new_cols = ["timestamp", "open", "high", "low", "close", "volume"]
df_stock.columns = new_cols


df_stock['timestamp'] = pd.to_datetime(df_stock['timestamp'])
df_stock['date'] = df_stock['timestamp'].dt.date

df_posts['timestamp'] = pd.to_datetime(df_posts['timestamp'])
df_posts['date'] = df_posts['timestamp'].dt.date

analyzer = SentimentIntensityAnalyzer()
df_posts["sentiment"] = df_posts['text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])

df_train = df_posts.groupby('date')['sentiment'].mean().reset_index()

# Combine stock closing prices and sentiment data for each day
df_stock['date'] = pd.to_datetime(df_stock['timestamp']).dt.date
df_train = df_train.merge(df_stock, on='date', how='left')

# Rename dataframe columns for Prophet to predict Stock using Sentiment
df_train.rename(columns={'date': 'ds', 'close': 'y'}, inplace=True)

# Train test split
df_test = df_train[df_train['ds'] >= pd.to_datetime('2025-03-15').date()]
df_train = df_train[df_train['ds'] < pd.to_datetime('2025-03-15').date()]


# Initialize and fit the Prophet model
model = Prophet()
model.add_regressor('sentiment')
model.fit(df_train)

# Create a DataFrame for future dates using df_test's dates and sentiment values
future_dates = df_test[['ds', 'sentiment']].copy()

# Predict the stock prices
forecast = model.predict(future_dates)
fig = model.plot(forecast)

# Add the actual stock prices from df_test to the matplotlib figure
ax = fig.gca()
ax.scatter(df_test['ds'], df_test['y'], color='red', label='Actual Stock Prices', s=10)


fig.show()

input()

