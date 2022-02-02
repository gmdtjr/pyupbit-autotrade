from dataclasses import asdict
import time
import pyupbit
import datetime
import schedule
import numpy as np
import math

access = ""          
secret = ""          

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
kkk = 0
now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

minute_pre = now.minute
# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        #print(now.minute, minute_pre)
        if (now.minute != minute_pre):
            kkk = kkk + 1
        schedule.run_pending()
        current_price = get_current_price(ticker)

        low_1 = float(df['low'][-2:-1])
        low_2 = float(df['low'][-3:-2])
        low_3 = float(df['low'][-4:-3])
        low_4 = float(df['low'][-5:-4])
        low_5 = float(df['low'][-6:-5])
        low_6 = float(df['low'][-7:-6])

        low_mean = (low_1 + low_2 + low_3)/3

        high_min = 999999999999999
        low_min = 999999999999999
        for i in range(-24,0):
            high_temp = float(df['high'][-1+i:0+i])
            if (high_min > high_temp):
                high_min = high_temp     
        for i in range(-24,0):
            low_temp = float(df['low'][-1+i:0+i])
            if (low_min > low_temp):
                low_min = low_temp         

        if (state == 0):
            if (current_price < low_mean and current_price > high_min):
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(ticker, krw*0.9995)
                    state = 1
                buy_price = current_price
                buy_hour = now.hour
                buy_minute = now.minute
                kkk = 0
                
        elif (state == 1):
            if (kkk <= 360): ## 1시간 경과
                percent = 0.03 - 0.03*(kkk/360)
                target_price = buy_price*(1+percent)
                percent = 0.01 - 0.01*(kkk/360)
                lower_price = buy_price*(1-percent)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                    kkk = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
                    kkk = 0
            else:
                buy_price = current_price
                buy_hour = now.hour
                buy_minute = now.minute
                state = 1
                kkk = 0
            
            if (current_price < low_min):
                btc = get_balance("BTC")
                if btc > 0:
                    upbit.sell_market_order(ticker, btc*0.9995)
                state = 0
                kkk = 0
                
        minute_pre = now.minute
        # Print
        iii = min(10, iii + 1)
        print("autotrade running", iii, '/ state: ', state)
        print(now.hour,'/',now.minute,'/',now.second)
        print(low_min, low_mean, current_price)
        #print(get_balance("BTC"))
        #print('kkk: ', kkk)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
