from alpha_vantage.timeseries import TimeSeries

def make_api_call(symbol, key):
    ts = TimeSeries(key=key, output_format='pandas')
    component_data, _ = ts.get_daily_adjusted(symbol, outputsize='full')
    component_data['symbol']=symbol
    component_data = component_data.reset_index()

    return component_data