import asyncio
import time
import pandas as pd

from alpaca_trade_api import Stream


min_bar_col_names = {"S": "symbol",
                     "o": "open",
                     "h": "high",
                     "l": "low",
                     "c": "close",
                     "v": "volume",
                     "t": "timestamp"
                     }

news_col_names = {"id": "id",
                  "headline": "headline",
                  "summary": "summary",
                  "author": "author",
                  "created_at": "created_at",
                  "updated_at": "updated_at",
                  "url": "url",
                  "content": "content",
                  "symbols": "symbols",
                  "source": "source"}


class LiveDataService:
    def __init__(self, tickers, conn, **kwargs):
        self.stream = Stream(**kwargs)
        self.tickers = tuple(tickers)
        self.conn = conn

    @staticmethod
    def format(t, names):
        return {names[k]: [v] for k, v in t.items() if k in names.keys()}

    def write(self, table, item):
        print(item)
        item.to_sql(table, self.conn, if_exists='append', index=False)

    async def bars_callback(self, t):
        t['id'] = str(t['t']) + t['S']
        t = self.format(t, min_bar_col_names)
        df = pd.DataFrame.from_dict(t)
        df['timestamp'] = pd.to_datetime(df['timestamp'].apply(lambda x: x.to_datetime()))
        df['id'] = df['timestamp'].astype('str') + '@' + df['symbol']
        self.write('min_bar_data', df)

    async def news_callback(self, t):
        t = self.format(t, news_col_names)
        df = pd.DataFrame.from_dict(t)
        df['created_at'] = pd.to_datetime(df['created_at'].apply(lambda x: x.to_datetime()))
        df['updated_at'] = pd.to_datetime(df['updated_at'].apply(lambda x: x.to_datetime()))
        self.write('news_data', df)

    def run_connection(self):
        try:
            self.stream.run()
        except KeyboardInterrupt:
            print("Interrupted execution by user")
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self.stream.stop_ws())
            exit(0)
        except Exception as e:
            print(f'Exception from websocket connection: {e}')
        finally:
            print("Trying to re-establish connection")
            time.sleep(3)
            self.run_connection()

    def run(self):
        self.stream.subscribe_news(self.news_callback, *self.tickers)
        self.stream.subscribe_bars(self.bars_callback, *self.tickers)

        self.run_connection()

