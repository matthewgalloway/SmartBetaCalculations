import config
from helpers import *
import pandas as pd
from api_setup import make_api_call
import time

def reset_header(df):
#   changes the first row of the df to the column names
    header_cols = df.iloc[0]
    df = df[1:]
    df.columns = header_cols
    return df

def get_html_table(url):
    return pd.read_html(url)[0]

def get_stocks_from_wiki(url):
    stocks_df = get_html_table(url)
    stocks_df = reset_header(stocks_df)
    return stocks_df

def get_stock_price(url):
    stocks_df = get_stocks_from_wiki(url)
    stocks_list = list(set(stocks_df.MMM))

    snp_components_timeseries = pd.DataFrame()
    failed_symbols =[]

    for symbol in stocks_list:
        try:
            time.sleep(1)
            component_data = make_api_call(symbol)
            snp_components_timeseries = snp_components_timeseries.append(component_data)
        except:
            failed_symbols.append(symbol)

    return snp_components_timeseries