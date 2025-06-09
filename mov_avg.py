import pandas as pd

import yfinance as yf

def fetch_stock_data_with_moving_average(ticker, start_date, end_date, ma_period=20):
# 주식 데이터 가져오기

    stock_data = yf.download(ticker, start=start_date, end=end_date)

# 이동평균 계산
    stock_data[f'MA_{ma_period}'] = stock_data['Close'].rolling(window=ma_period).mean()

    return stock_data