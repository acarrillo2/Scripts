import pandas as pd
from utils import date_generator
from data_retriever import data_retriever
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.dates as mdates

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

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

def build_vs_last_columns(df):
    df_vs_last = df.reset_index()
    df_vs_last.drop(inplace=True, columns=['index'])
    df_vs_last['vs last'] = 0
    df_vs_last['vs last %'] = 0
    for i in range(len(df)):
        if i == 0:
            pass
        else:
            df_vs_last.loc[i, 'vs last'] = df_vs_last.loc[i, 'Value'] - df_vs_last.loc[i-1, 'Value']
            df_vs_last.loc[i, 'vs last %'] = ((df_vs_last.loc[i, 'Value'] - df_vs_last.loc[i-1, 'Value']) / df_vs_last.loc[i-1, 'Value'])
    return df_vs_last

def build_portfolio_performance(df):
    df_portfolio = build_vs_last_columns(df)
    df_portfolio = df_portfolio.tail(1)
    return df_portfolio

def build_stock_performance(df):
    df_stock = build_vs_last_columns(df)
    last_date = df_stock.loc[len(df_stock)-1, 'Date']
    df_stock = df_stock[df_stock['Date'] == last_date]
    df_stock = df_stock[['Ticker', 'Close', 'Date', 'Quantity', 'Value', 'vs last', 'vs last %']]
    return df_stock

def save_graph(df, title):
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
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

def convert_to_html(df):
    return df.to_html(
        index=False,
        formatters={
            'Close': '${0:,.2f}'.format,
            'Value': '${0:,.2f}'.format,
            'vs last': '${0:,.2f}'.format,
            'vs last %': '{:,.2%}'.format
        }
    )

def main():
    print("start")
    plt.close('all')
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template("/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/html/master_template.html")
    file_path = "stock_portfolio/portfolio_data/portfolio_small.csv"
    six_months_ago = date_generator.get_six_months_ago().strftime("%Y-%m-%d")
    df = data_retriever.gather_stock_quotes(six_months_ago, file_path)

    # Weekly
    print('## Weekly Data')
    df_weekly_data = filter_t8_weeks_stock_quotes(df)
    print(df_weekly_data)
    df_weekly_agg = aggregate_dataframe(df_weekly_data)
    print(df_weekly_agg)
    save_graph(df_weekly_agg, 'T8_Weekly_Performance')
    df_weekly_portfolio = build_portfolio_performance(df_weekly_agg)
    print(df_weekly_portfolio)
    df_weekly_stock = build_stock_performance(df_weekly_data)
    print(df_weekly_stock)

    # Monthly
    print('## Monthly Data')
    df_monthly_data = filter_t6_months_stock_quotes(df)
    df_monthly_agg = aggregate_dataframe(df_monthly_data)
    print(df_monthly_agg)
    save_graph(df_monthly_agg, 'T6_Monthly_Performance')
    df_monthly_portfolio = build_portfolio_performance(df_monthly_agg)
    print(df_monthly_portfolio)
    df_monthly_stock = build_stock_performance(df_monthly_data)
    print(df_monthly_stock)

    template_vars = {"title" : "Stock Report",
                "weekly_portfolio_performance": convert_to_html(df_weekly_portfolio),
                "weekly_stock_performance": convert_to_html(df_weekly_stock),
                "monthly_portfolio_performance": convert_to_html(df_monthly_portfolio),
                "monthly_stock_performance": convert_to_html(df_monthly_stock)}
    html_out = template.render(template_vars)
    HTML(
        string=html_out, 
        base_url='/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/').write_pdf("/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/report.pdf", 
        stylesheets=['/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/css/style.css']
        )

    


if __name__ == "__main__":
    main()