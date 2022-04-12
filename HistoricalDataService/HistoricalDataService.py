from alpaca_trade_api.rest import REST, TimeFrame, TimeFrameUnit
import pandas as pd
from sqlalchemy import text
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


class HistoricalDataService:
    def __init__(self, **kwargs):
        self.api = REST(**kwargs)

    def get_bars_symbol(self, symbols, start, stop, interval=TimeFrame.Hour, adjustment='raw'):
        df = pd.DataFrame(self.api.get_bars(symbols, interval, start, stop, adjustment=adjustment).df)
        df.reset_index(drop=False, inplace=True)
        df['id'] = df['timestamp'].astype('str') + '@' + df['symbol']
        df = df[['id', 'symbol', 'timestamp', 'open', 'high', 'low', 'close', 'volume']]
        return df.drop_duplicates('id', keep='first')

    def get_news(self, symbols, start, stop, limit):
        news = self.api.get_news(symbols,
                                 start=start,
                                 end=stop,
                                 limit=limit,
                                 include_content=True,
                                 exclude_contentless=True
                                 )
        news = map(lambda x: x._raw, news)
        df = pd.DataFrame(news).drop(columns=['images'])
        df['created_at'] = pd.to_datetime(df['created_at'])
        df['updated_at'] = pd.to_datetime(df['updated_at'])
        df = df[
            ['id',
             'symbols',
             'created_at',
             'updated_at',
             'headline',
             'summary',
             'content',
             'author',
             'url',
             'source'
             ]
        ]
        return df.drop_duplicates('id', keep='first')


if __name__ == '__main__':
    # To be ran once
    import sqlalchemy
    import json
    import yaml
    from tqdm import tqdm

    with open('../Config/keys.json', 'r') as f:
        config = json.load(f)
        alpaca_config = config['alpaca']['paper trading acct']
        db_config = config['postgres']
    with open('../Config/tickers.yml', 'r') as f:
        tickers = yaml.load(f, Loader=yaml.Loader)['tickers']
    hds = HistoricalDataService(key_id=alpaca_config['API_KEY'],
                                secret_key=alpaca_config['API_SECRET'],
                                base_url=alpaca_config['BASE_URL'],
                                raw_data=True
                                )
    _start = '2016-01-01'
    _stop = '2021-04-12'
    _limit = 10000
    dates = pd.date_range(_start, _stop, freq='1M').astype('str')
    engine = sqlalchemy.create_engine(f'postgresql://' +
                                      f'{db_config["user"]}' +
                                      f':{db_config["password"]}' +
                                      f'@{db_config["host"]}' +
                                      f':{db_config["port"]}')
    for begin, end in tqdm(list(zip(dates[:-1], dates[1:]))):
        news = hds.get_news(tickers, begin, end, _limit)
        bars = hds.get_bars_symbol(tickers, begin, end, interval=TimeFrame(1, TimeFrameUnit.Minute))
        bars.to_sql('min_bar_data_temp', engine, if_exists='replace', index=False)
        news.to_sql('news_data_temp', engine,
                    if_exists='append',
                    index=False,
                    dtype={'id': sa.Integer(),
                           'symbols': postgresql.ARRAY(sa.String),
                           'created_at': sa.DateTime(),
                           'updated_at': sa.DateTime(),
                           'headline': sa.Text(),
                           'summary': sa.Text(),
                           'content': sa.Text(),
                           'author': sa.Text(),
                           'url': sa.Text(),
                           'source': sa.Text()
                           }
                    )
        with engine.begin() as conn:
            # '(id, symbols, created_at, updated_at, headline, summary, content, author, url, source) ' \
            # '(id, symbol, timestamp, open, high, low, close, volume) ' \
            insert_bars = 'INSERT INTO min_bar_data SELECT * ' \
                          'FROM min_bar_data_temp ON CONFLICT (id) DO NOTHING;'
            insert_news = 'INSERT INTO news_data (id, symbols, created_at, updated_at, headline, summary, content, author, url, source) ' \
                          'SELECT id, symbols::text, created_at, updated_at, headline, summary, content, author, url, source ' \
                          'FROM news_data_temp ON CONFLICT (id) DO NOTHING;'
            conn.execute(text(insert_news))
            conn.execute(text(insert_bars))
    with engine.begin() as conn:
        drop = 'DROP TABLE IF EXISTS min_bar_data_temp, news_data_temp;'
