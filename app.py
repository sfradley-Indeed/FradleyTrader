import os

import yaml
from celery import Celery
from flask import Flask
from flask_crontab import Crontab
import json

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from LiveDataService.LiveDataService import LiveDataService

with open('Config/keys.json', 'r') as f:
    config = json.load(f)
alpaca_config = config['alpaca']['paper trading acct']
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{config["postgres"]["user"]}' \
                                        f':{config["postgres"]["password"]}' \
                                        f'@{config["postgres"]["host"]}' \
                                        f':{config["postgres"]["port"]}'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
crontab = Crontab(app)


def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=os.environ.get('BROKER_URL'), backend=os.environ.get('BACKEND_URL'),
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


def stream():
    with open('Config/tickers.yml', 'r') as f:
        tickers = yaml.load(f, Loader=yaml.Loader)['tickers']
    engine = db.get_engine(app)
    with engine.connect() as conn:
        lds = LiveDataService(tickers,
                              conn,
                              key_id=alpaca_config['API_KEY'],
                              secret_key=alpaca_config['API_SECRET'],
                              base_url=alpaca_config['BASE_URL'],
                              data_feed=alpaca_config['FEED'],
                              raw_data=True
                              )
        lds.run()


stream()

if __name__ == '__main__':
    app.run()
