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

def build_portfolio_performance(df):
    df_portfolio = df.reset_index()
    df_portfolio.drop(inplace=True, columns=['index'])
    df_portfolio['vs last'] = 0
    df_portfolio['vs last %'] = 0
    for i in range(len(df)):
        if i == 0:
            pass
        else:
            df_portfolio.loc[i, 'vs last'] = df_portfolio.loc[i, 'Value'] - df_portfolio.loc[i-1, 'Value']
            df_portfolio.loc[i, 'vs last %'] = round(((df_portfolio.loc[i, 'Value'] - df_portfolio.loc[i-1, 'Value']) / df_portfolio.loc[i-1, 'Value']) * 100, 1)
    return df_portfolio.tail(1)


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


def main():
    print("start")
    plt.close('all')
    env = Environment(loader=FileSystemLoader('/'))
    template = env.get_template("/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/html/master_template.html")
    file_path = "stock_portfolio/portfolio_data/portfolio_small.csv"
    six_months_ago = date_generator.get_six_months_ago().strftime("%Y-%m-%d")
    df = data_retriever.gather_stock_quotes(six_months_ago, file_path)

    # Weekly
    df_weekly_data = filter_t8_weeks_stock_quotes(df)
    df_weekly_agg = aggregate_dataframe(df_weekly_data)
    print(df_weekly_agg)
    save_graph(df_weekly_agg, 'T8_Weekly_Performance')
    df_weekly_portfolio = build_portfolio_performance(df_weekly_agg)
    print(df_weekly_portfolio)

    # Monthly
    df_monthly_portfolio = filter_t6_months_stock_quotes(df)
    df_monthly_agg = aggregate_dataframe(df_monthly_portfolio)
    print(df_monthly_agg)
    save_graph(df_monthly_agg, 'T6_Monthly_Performance')
    df_monthly_portfolio = build_portfolio_performance(df_monthly_agg)
    print(df_monthly_portfolio)

    template_vars = {"title" : "Stock Report",
                "weekly_portfolio_performance": df_weekly_portfolio.to_html(index=False),
                "weekly_stock_performance": "Placeholder",
                "monthly_portfolio_performance": df_monthly_portfolio.to_html(index=False),
                "monthly_stock_performance": "Placeholder"}
    html_out = template.render(template_vars)
    HTML(
        string=html_out, 
        base_url='/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/').write_pdf("/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/report.pdf", 
        stylesheets=['/Users/austin/workspace/Scripts/src/Scripts/stock_portfolio/css/style.css']
        )

    


if __name__ == "__main__":
    main()