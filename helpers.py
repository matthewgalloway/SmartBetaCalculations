import config
from helpers import *
import pandas as pd


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