from flask import Flask
from flask_crontab import Crontab
import json

with open('Config/keys.json', 'r') as f:
    config = json.load(f)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] =
crontab = Crontab(app)


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@crontab.job()
def populate_stock_data():
    with open('./Config/tickers.yml', 'r') as f:
        tickers = json.load(f)['tickers']



if __name__ == '__main__':
    app.run()
