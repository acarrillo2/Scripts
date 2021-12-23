import pandas as pd
import yfinance as yf
from datetime import datetime
from dateutil.relativedelta import relativedelta

def gather_stock_quotes(start_date, file_path):
    portfolio = pd.read_csv(file_path)
    end_date = datetime.now().strftime("%Y-%m-%d")
    df_final = pd.DataFrame(index=["Date"], columns=["Close", "Ticker", "Quantity", "Value"])
    for index, row in portfolio.iterrows():
        tickerData = yf.Ticker(row["Ticker"])
        tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)
        df = tickerDf[["Close"]]
        df["Ticker"] = row["Ticker"]
        df["Quantity"] = row["Quantity"]
        df["Value"] = df["Quantity"] * df["Close"]
        df_final = pd.concat([df_final, df])
    df_final.dropna(inplace=True)
    df_final.index = pd.to_datetime(df_final.index)
    return df_final

def get_single_stock_quote(start_date, ticker):
    end_date = datetime.now().strftime("%Y-%m-%d")
    tickerData = yf.Ticker(ticker)
    tickerDf = tickerData.history(period='1d', start=start_date, end=end_date)
    df = tickerDf[["Close"]]
    df.index.name = None
    df.rename(columns={"Close": "Value"}, inplace=True)
    return df

def main():
    six_months_ago = (datetime.now() - relativedelta(months=6)).strftime("%Y-%m-%d")
    df = get_single_stock_quote(six_months_ago, "SPY")
    print(df)

if __name__ == "__main__":
    main()