import pandas as pd
from utils import date_generator
from data_retriever import data_retriever
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates

def filter_t8_weeks_stock_quotes(df):
    df_max_date = df
    df_max_date['Week_Number'] = df_max_date.index.isocalendar().week
    df_max_date['Date'] = df_max_date.index
    df_max_date = df.groupby(['Week_Number']).max()
    t8_week_end_dates = df_max_date['Date'].tolist()
    t8_week_end_dates = t8_week_end_dates[-8:]
    return df[df.index.isin(t8_week_end_dates)]

def filter_t6_months_stock_quotes(df):
    df_max_date = df
    df_max_date['Month'] = df_max_date.index.month
    df_max_date['Date'] = df_max_date.index
    df_max_date = df.groupby(['Month']).max()
    t6_month_end_dates = df_max_date['Date'].tolist()
    t6_month_end_dates = t6_month_end_dates[-6:]
    return df[df.index.isin(t6_month_end_dates)]

def aggregate_dataframe(df):
    df = df[["Value"]]
    return df.groupby(df.index).sum()


def save_graph(df, title):
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    df.plot(kind='line', title=title,
            color='blue', ax=ax)

    fmt = '${x:,.0f}'
    tick = mtick.StrMethodFormatter(fmt)
    ax.yaxis.set_major_formatter(tick) 
    ## This kept spitting out random dates in 1977, maybe input data is bad?
    # myFmt = mdates.DateFormatter('%Y-%m-%d')
    # ax.xaxis.set_minor_formatter(myFmt)
    plt.xticks(rotation=25)

    # plt.show()
    plt.savefig('/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/images/'+title+'.png')


def main():
    print("start")
    file_path = "stock_portfolio/portfolio_data/portfolio_small.csv"
    six_months_ago = date_generator.get_six_months_ago().strftime("%Y-%m-%d")
    df = data_retriever.gather_stock_quotes(six_months_ago, file_path)

    # Weekly
    df_weekly_portfolio = filter_t8_weeks_stock_quotes(df)
    df_weekly_agg = aggregate_dataframe(df_weekly_portfolio)
    print(df_weekly_agg)
    save_graph(df_weekly_agg, 'T8_Weekly_Performance')

    # Monthly
    df_monthly_portfolio = filter_t6_months_stock_quotes(df)
    df_monthly_agg = aggregate_dataframe(df_monthly_portfolio)
    print(df_monthly_agg)
    save_graph(df_monthly_agg, 'T6_Monthly_Performance')

    


if __name__ == "__main__":
    main()