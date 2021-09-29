import config
from helpers import *
import pandas as pd
from api_setup import make_api_call
import time
from dataiku import pandasutils as pdu
import dataiku

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

def rename_columns(df):
    df_cols = df.columns
    new_df_cols = []
    for col in df_cols:
        if len(col.split())>1:
            new_df_cols.append(col.split()[1])
        else:
            new_df_cols.append(col)
    df.columns = new_df_cols
    df.rename(columns={'adjusted':'adjusted_close'},inplace=True)
    return df

def breakdown_by_ticker(variable, df):
    var_df = df.reset_index().pivot(index='date', columns='symbol', values=variable)
    return var_df

def get_stock_price(url, key):
    stocks_df = get_stocks_from_wiki(url)
    stocks_list = list(set(stocks_df.MMM))

    snp_components_timeseries = pd.DataFrame()
    failed_symbols =[]

    for symbol in stocks_list:
        try:
            component_data = make_api_call(symbol, key)
            snp_components_timeseries = snp_components_timeseries.append(component_data)
            time.sleep(1)
        except:
            failed_symbols.append(symbol)

    snp_components_timeseries = rename_columns(snp_components_timeseries)
    snp_components_timeseries = breakdown_by_ticker('adjusted_close', snp_components_timeseries)

    return snp_components_timeseries

def calc_cumilative_weighted_returns(returns, weights):
    weighted_returns = returns * weights
    daily_returns = weighted_returns.sum(axis=1)
    cumulative_returns = 1 + daily_returns.cumsum()
    return pd.DataFrame(cumulative_returns)


def get_input_data_and_set_date_index(var, set_date=True):
    dk_obj = dataiku.Dataset(var)
    df = dk_obj.get_dataframe()
    if set_date:
        df.set_index('date',inplace=True)
    return df