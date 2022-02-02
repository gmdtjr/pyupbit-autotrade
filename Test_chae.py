from dataclasses import asdict
import time
import pyupbit
import datetime
import schedule
import numpy as np
import math

access = ""          # 본인 값으로 변경
secret = ""          # 본인 값으로 변경

def get_balance(ticker):
    #"""잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    #"""현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 사용 거래소 기록 가져오기
df = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count = 50)
ticker = "KRW-BTC"

# 초기 flag setting
state = 0 ## 0: 모두 현금, 1: 모두 BTC
buy_price = 0
target_price = 0.0
lower_price = 0.0
iii = 0

now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

close_min = 999999999999999
for i in range(-24,0):
    close_temp = float(df['high'][-1+i:0+i])
    if (close_min > close_temp):
        close_min = close_temp
        
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        schedule.run_pending()
        current_price = get_current_price(ticker)

        close_1 = float(df['close'][-2:-1])
        close_2 = float(df['close'][-3:-2])
        close_3 = float(df['close'][-4:-3])
        close_4 = float(df['close'][-5:-4])
        close_5 = float(df['close'][-6:-5])
        close_6 = float(df['close'][-7:-6])

        close_mean = (close_1 + close_2 + close_3 + close_4 + close_5 + close_6)/6

        high_min = 999999999999999
        close_min = 999999999999999
        for i in range(-24,0):
            high_temp = float(df['high'][-1+i:0+i])
            if (high_min > high_temp):
                high_min = high_temp     
        for i in range(-24,0):
            close_temp = float(df['close'][-1+i:0+i])
            if (close_min > close_temp):
                close_min = close_temp         
        print(close_min, close_mean, current_price)

        # Print
        iii = iii + 1
        print("autotrade running", iii, '/ state: ', state)
        print(now.hour,'/',now.minute,'/',now.second)
        print(get_balance("BTC"))
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
