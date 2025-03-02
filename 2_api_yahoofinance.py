import logging
import pickle
from datetime import datetime, timedelta, time

import pandas as pd
import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# логирование в файл
file_handler = logging.FileHandler('yf_stocks_api.log')
file_handler.setLevel(logging.INFO)
file_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

# логирование в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s %(levelname)s:%(message)s')
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

with open('to_check.pkl', 'rb') as file:
    to_check = pickle.load(file)

# запросы для получения stock_info проводились по permalink вместо stock_id, поэтому надо сматчить
# без drop_duplicates в df_stock_info создаются дубликаты для каждого значения датафрейма цен
df_prices_ww = pd.read_parquet('prices_ww.parquet')[['stock_id', 'stock_permalink']].drop_duplicates()
df_stock_info = pd.read_parquet('info.parquet')[['permalink', 'yahoo_finance_link']]
df_stock_info = df_stock_info.merge(df_prices_ww, left_on='permalink', right_on='stock_permalink', how='left')

data = []
for stock_id, yahoo_finance_link in df_stock_info[df_stock_info['stock_id'].isin(to_check)][['stock_id', 'yahoo_finance_link']].itertuples(index=False):
    ticker = yahoo_finance_link.split('=')[1]
    logging.info(f"Processing ticker: {ticker} (stock_id: {stock_id})")

    # 2022-10-03 - самая старая дата, по которой есть цены - без подписки на whalewisdom доступны ~2.5 года исторических цен
    start_seconds = int(datetime.strptime('2022-10-03', '%Y-%m-%d').timestamp())
    end_seconds = int((datetime.now() + timedelta(10)).timestamp())

    try:
        # запросы с пустым User-Agent отклоняются (по умолчанию он ставится питоновским), поэтому надо передать хоть что-то - zip
        resp = requests.get(
            f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}',
            headers={'User-Agent': 'zip'},
            params={'period1': start_seconds, 'period2': end_seconds, 'interval': '1d'},
            timeout=5
        ).json()
        resp = resp['chart']['result'][0]
        df = pd.DataFrame({
            # questionable подход с datetime вместо date, но оно работает (не ломается из-за временных поясов, например) и удобно сопоставляется с ww ценами
            'date': [datetime.combine(datetime.fromtimestamp(d).date(), time(0, 0, 0)) for d in resp['timestamp']],
            'closing_price': resp['indicators']['adjclose'][0]['adjclose']
        })
        df['stock_id'] = stock_id
        df['yf_ticker'] = ticker
        data.append(df)
        logging.info(f"Data collected for ticker: {ticker}, stock_id: {stock_id}")
    except Exception as e:
        logging.error(f"Failed to retrieve data for ticker: {ticker}, stock_id: {stock_id}. Error: {e}")

df = pd.concat(data)
df.to_parquet('yf_prices.parquet')
# df.to_excel('yf_prices.xlsx')
logging.info("Data saved to 'yf_prices.parquet'.")
