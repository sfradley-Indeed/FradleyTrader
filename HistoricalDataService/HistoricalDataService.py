from alpaca_trade_api.rest import REST, TimeFrame
import pandas as pd


class HistoricalDataService:
    def __init__(self, **kwargs):
        self.api = REST(**kwargs)

    def get_bars_symbol(self, symbols, start, stop, interval=TimeFrame.Hour, adjustment='raw'):
        df = self.api.get_bars(symbols, interval, start, stop, adjustment=adjustment).df
        return df


if __name__ == '__main__':
    import json
    with open('../Config/keys.json', 'r') as f:
        config = json.load(f)['alpaca']['paper trading acct']
    hds = HistoricalDataService(key_id=config['API_KEY'],
                                secret_key=config['API_SECRET'],
                                base_url=config['BASE_URL'],
                                raw_data=True
                                )
    df = pd.DataFrame(hds.get_bars_symbol(['AAPL', 'TSLA', 'SPY'], '2016-01-01', '2017-01-01'))
    print(len(df))
    print(df.head())
    print(df.tail())
