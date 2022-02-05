import os
import sys
from utils import date_generator
from data_retriever import data_retriever
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

sys.path.append('/home/austin/workplace')
sys.path.append('/Users/austin/workspace')
from python_modules.email_helper import send_email

def filter_t8_weeks_stock_quotes(df):
    df_max_date = df
    df_max_date['Week_Number'] = df_max_date.index.isocalendar().week
    df_max_date['Date'] = df_max_date.index
    pd.set_option("display.max_rows", None, "display.max_columns", None)
    df_max_date = df_max_date.groupby(['Week_Number']).max()
    df_max_date.reset_index(inplace=True)
    df_max_date.index = df_max_date['Date']
    df_max_date.sort_index(inplace=True)
    t8_week_end_dates = df_max_date.index.tolist()
    t8_week_end_dates = t8_week_end_dates[-8:]   
    return df[df.index.isin(t8_week_end_dates)]  

def filter_t6_months_stock_quotes(df):
    df_max_date = df
    df_max_date['Month'] = df_max_date.index.month
    df_max_date['Date'] = df_max_date.index
    df_max_date = df.groupby(['Month']).max()
    df_max_date.reset_index(inplace=True)
    df_max_date.index = df_max_date['Date']
    df_max_date.sort_index(inplace=True)
    t6_month_end_dates = df_max_date['Date'].tolist()
    t6_month_end_dates = t6_month_end_dates[-6:]
    return df[df.index.isin(t6_month_end_dates)] # So this will give me highest months not latest months
                                                 # We need to do a similar thing as we did in week so that we sort by date then filter

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

def build_stock_performance(df):
    df_stock = build_vs_last_columns(df)
    last_date = df_stock.loc[len(df_stock)-1, 'Date']
    df_stock = df_stock[df_stock['Date'] == last_date]
    df_stock = df_stock[['Ticker', 'Close', 'Date', 'Quantity', 'Value', 'vs last', 'vs last %']]
    return df_stock.sort_values(by=['Value'], ascending=False)

def build_index_performance(df_index, df_portfolio):
    df_index['S&P 500'] = 100
    df_index['Portfolio'] = 100
    df_index['p vs last'] = df_portfolio['vs last']
    df_index['p vs last %'] = df_portfolio['vs last %']
    for i in range(len(df_index)):
        if i == 0:
            pass
        else:
            df_index.loc[i, 'S&P 500'] = (df_index.loc[i, 'vs last %'] * df_index.loc[i-1, 'S&P 500']) + df_index.loc[i-1, 'S&P 500']
            df_index.loc[i, 'Portfolio'] = (df_index.loc[i, 'p vs last %'] * df_index.loc[i-1, 'Portfolio']) + df_index.loc[i-1, 'Portfolio']
    df_index.set_index(['Date'], inplace=True)
    df_index.index.name = None
    df_index = df_index[['S&P 500', 'Portfolio']]
    return df_index

def build_t8_stock_performance(df, df_t8_weekly_portfolio):
    df.reset_index(inplace=True)
    first_date = df.loc[0, 'Date']
    last_date = df.loc[len(df)-1, 'Date']
    df = df[(df['Date'] == first_date) | (df['Date'] == last_date)]
    df = build_vs_last_columns(df)
    df = df[['Ticker', 'Close', 'Date', 'Quantity', 'Value', 'vs last', 'vs last %']]
    df = df[df['Date'] == last_date]
    df['% of tot'] = df['vs last'] / df_t8_weekly_portfolio.loc[1, 'vs last']
    df['bps'] = round(df['% of tot'] * df_t8_weekly_portfolio.loc[1, 'vs last %'] * 10000,0)
    if (df_t8_weekly_portfolio.loc[1, 'vs last'] < 0):
        df.sort_values(by=['bps'], ascending=True, inplace=True)
    else:
        df.sort_values(by=['bps'], ascending=False, inplace=True)
    df.drop(columns=['% of tot'], inplace=True)
    return df

def build_t8_portfolio_performance(df):
    df.reset_index(inplace=True)
    first_date = df.loc[0, 'index']
    last_date = df.loc[len(df)-1, 'index']
    df = df[(df['index'] == first_date) | (df['index'] == last_date)]
    df = build_vs_last_columns(df)
    df = df[['Value', 'vs last', 'vs last %']]
    return df[df.index.isin([1])]

def save_graph(df, title, currency=False):
    fig, ax = plt.subplots(1, 1, figsize=(6, 4))
    df.plot(kind='line', title=title,ax=ax)
    if currency == True:
        fmt = '${x:,.0f}'
        tick = mtick.StrMethodFormatter(fmt)
        ax.yaxis.set_major_formatter(tick)
    plt.xticks(rotation=25)
    plt.savefig('stock_portfolio/images/'+title+'.png')

def convert_to_html(df):
    return df.to_html(
        index=False,
        formatters={
            'Close': '${0:,.2f}'.format,
            'Value': '${0:,.2f}'.format,
            'vs last': '${0:,.2f}'.format,
            'vs last %': '{:,.2%}'.format,
            'bps': '{:,.0f}'.format
        }
    )

def main():
    plt.close('all')
    env = Environment(loader=FileSystemLoader(os.getcwd() + '/stock_portfolio/html'))
    template = env.get_template("master_template.html")
    file_path = "stock_portfolio/portfolio_data/portfolio.csv"
    six_months_ago = date_generator.get_six_months_ago().strftime("%Y-%m-%d")
    df = data_retriever.gather_stock_quotes(six_months_ago, file_path)
    df_sp500 = data_retriever.get_single_stock_quote(six_months_ago, "SPY")

    # Weekly
    df_weekly_data = filter_t8_weeks_stock_quotes(df)
    df_weekly_sp500 = filter_t8_weeks_stock_quotes(df_sp500)
    df_weekly_agg = aggregate_dataframe(df_weekly_data)
    save_graph(df_weekly_agg, 'T8_Weekly_Performance', currency=True)
    df_weekly_vs_last = build_vs_last_columns(df_weekly_agg)
    df_weekly_portfolio = df_weekly_vs_last.tail(1)
    df_weekly_stock = build_stock_performance(df_weekly_data)
    df_weekly_sp500_vs_last = build_vs_last_columns(df_weekly_sp500)
    df_weekly_index = build_index_performance(df_weekly_sp500_vs_last, df_weekly_vs_last)
    save_graph(df_weekly_index, 'T8_Weekly_Indexed_Performance')
    df_t8_weekly_portfolio = build_t8_portfolio_performance(df_weekly_agg)
    df_t8_weekly_stock = build_t8_stock_performance(df_weekly_data, df_t8_weekly_portfolio)

    # Monthly
    df_monthly_data = filter_t6_months_stock_quotes(df)
    df_monthly_sp500 = filter_t6_months_stock_quotes(df_sp500)
    df_monthly_agg = aggregate_dataframe(df_monthly_data)
    save_graph(df_monthly_agg, 'T6_Monthly_Performance', currency=True)
    df_monthly_vs_last = build_vs_last_columns(df_monthly_agg)
    df_monthly_portfolio = df_monthly_vs_last.tail(1)
    df_monthly_stock = build_stock_performance(df_monthly_data)
    df_monthly_sp500_vs_last = build_vs_last_columns(df_monthly_sp500)
    df_monthly_index = build_index_performance(df_monthly_sp500_vs_last, df_monthly_vs_last)
    save_graph(df_monthly_index, 'T6_Monthly_Indexed_Performance')
    df_t6_monthly_portfolio = build_t8_portfolio_performance(df_monthly_agg)
    df_t6_monthly_stock = build_t8_stock_performance(df_monthly_data, df_t6_monthly_portfolio)

    template_vars = {"title" : "Stock Report",
                "weekly_portfolio_performance": convert_to_html(df_t8_weekly_portfolio),
                "weekly_stock_performance": convert_to_html(df_t8_weekly_stock),
                "weekly_portfolio_performance_last_week": convert_to_html(df_weekly_portfolio),
                "weekly_stock_performance_last_week": convert_to_html(df_weekly_stock),
                "monthly_portfolio_performance": convert_to_html(df_t6_monthly_portfolio),
                "monthly_stock_performance": convert_to_html(df_t6_monthly_stock),
                "monthly_portfolio_performance_last_month": convert_to_html(df_monthly_portfolio),
                "monthly_stock_performance_last_month": convert_to_html(df_monthly_stock)}
    html_out = template.render(template_vars)
    HTML(
        string=html_out, 
        base_url=os.getcwd() + 'stock_portfolio').write_pdf(os.getcwd() + '/stock_portfolio/report.pdf', 
        stylesheets=[os.getcwd() + '/stock_portfolio/css/style.css']
        )
    send_email(recipients=['acarrillogu@gmail.com'], CC=[], BCC=[], subject="Weekly Stock Report", 
    message="Weekly Stock Report", file_list=[os.getcwd() + '/stock_portfolio/report.pdf'])

    


if __name__ == "__main__":
    main()