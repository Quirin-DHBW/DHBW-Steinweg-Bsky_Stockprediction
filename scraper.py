import sys, os
os.chdir(os.path.dirname(sys.argv[0]))

# The official Bluesky API accessing package
from atproto import Client

import duckdb
from datetime import *
from time import sleep
import pandas as pd
import yfinance as yf

SINCE = datetime(year=2024, month=1, day=1)
UNTIL = datetime(year=2025, month=4, day=30)
SINCE_TXT = SINCE.strftime("%Y%m%d")
UNTIL_TXT = UNTIL.strftime("%Y%m%d")
STOCK = "TSLA"
SEARCH_TERMS = ["Tesla", "Elon Musk", "electric", "car"]
POSTS_PER_DAY = 10

DO_STOCK_FETCH = True
DO_POST_FETCH = True


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

if DO_STOCK_FETCH:
    stock_df = fetch_stock_data(STOCK, start_date=SINCE.strftime("%Y-%m-%d"), end_date=UNTIL.strftime("%Y-%m-%d"))

    with duckdb.connect(f"{STOCK}_{SINCE_TXT}_{UNTIL_TXT}_stock.db") as db:
        db.execute("CREATE TABLE stock_values AS SELECT * FROM stock_df")
        db.execute("INSERT INTO stock_values SELECT * FROM stock_df")


if DO_POST_FETCH:
    print("Logging in to Bluesky...")
    client = Client()
    with open("login.txt", "r") as login:
        creds = login.read().split("\n")
        #print(creds)
        client.login(creds[0], creds[1])

    with duckdb.connect(f"{STOCK}_{SINCE_TXT}_{UNTIL_TXT}_posts.db") as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                timestamp TIMESTAMPTZ,
                text TEXT,
                uri TEXT,
                like_count INTEGER,
                quote_count INTEGER,
                reply_count INTEGER,
                repost_count INTEGER
            )
        """)
        for term in SEARCH_TERMS:
            for day in days:
                print(f"Pulling posts for {term} on {day[0]}...", end="\r")
                resp = None
                resp_success = False
                while not resp_success:
                    resp = client.app.bsky.feed.search_posts(params={"q":term, 
                                                                    "limit":POSTS_PER_DAY,
                                                                    "sort":"top",
                                                                    "since":f"{day[0]}T00:00:00.000Z",
                                                                    "until":f"{day[1]}T00:00:00.000Z"
                                                                    }
                                                            )
                    
                    try:
                        test = resp.posts[0].record.created_at
                        resp_success = True
                    except:
                        print("Pull unsuccessful, retrying in a second...", end="\r")
                        sleep(2)
                        continue
                

                # This part is for directly writing it into the db
                print("\nInserting posts into DB...")
                for post in resp.posts:
                    timestamp = post.record.created_at
                    text = post.record.text
                    uri = post.uri
                    like_count = post.like_count
                    quote_count = post.quote_count
                    reply_count = post.reply_count
                    repost_count = post.repost_count

                    db.execute("""
                        INSERT INTO posts (timestamp, text, uri, like_count, quote_count, reply_count, repost_count)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (timestamp, text, uri, like_count, quote_count, reply_count, repost_count))
        print("Finished pulling posts.")

