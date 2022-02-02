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

close_1 = float(df['close'][-2:-1])
close_2 = float(df['close'][-3:-2])
close_3 = float(df['close'][-4:-3])
close_4 = float(df['close'][-5:-4])
close_5 = float(df['close'][-6:-5])
close_6 = float(df['close'][-7:-6])
current_price = get_current_price(ticker)
close_mean = (close_1 + close_2 + close_3 + close_4 + close_5 + close_6)/6

close_min = 999999999999999
for i in range(-24,0):
    close_temp = float(df['high'][-1+i:0+i])
    if (close_min > close_temp):
        close_min = close_temp
        
print(close_min, close_mean, current_price)
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

        if (state == 0):
            if (current_price < close_mean and current_price > high_min):
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(ticker, krw*0.9995)
                    state = 1
            
            buy_price = current_price
            buy_hour = now.hour
            buy_minute = now.minute
            
        elif (state == 1):
            if ((now.hour == buy_hour and now.minute >= buy_minute) or (now.hour == ((buy_hour+1)%24) and now.minute < buy_minute)): ## 1시간 경과
                target_price = buy_price*(1+0.01)
                lower_price = buy_price*(1-0.01)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            elif ((now.hour == ((buy_hour+1)%24) and now.minute >= buy_minute) or (now.hour == ((buy_hour+2)%24) and now.minute < buy_minute)): ## 2시간 경과
                target_price = buy_price*(1+0.009)
                lower_price = buy_price*(1-0.009)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            elif ((now.hour == ((buy_hour+2)%24) and now.minute >= buy_minute) or (now.hour == ((buy_hour+3)%24) and now.minute < buy_minute)): ## 3시간 경과
                target_price = buy_price*(1+0.008)
                lower_price = buy_price*(1-0.008)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            elif ((now.hour == ((buy_hour+3)%24) and now.minute >= buy_minute) or (now.hour == ((buy_hour+4)%24) and now.minute < buy_minute)): ## 4시간 경과
                target_price = buy_price*(1+0.007)
                lower_price = buy_price*(1-0.007)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            elif ((now.hour == ((buy_hour+4)%24) and now.minute >= buy_minute) or (now.hour == ((buy_hour+5)%24) and now.minute < buy_minute)): ## 5시간 경과
                target_price = buy_price*(1+0.006)
                lower_price = buy_price*(1-0.006)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            elif ((now.hour == ((buy_hour+5)%24) and now.minute >= buy_minute) or (now.hour == ((buy_hour+6)%24) and now.minute < buy_minute)): ## 6시간 경과
                target_price = buy_price*(1+0.005)
                lower_price = buy_price*(1-0.005)
                if (current_price > target_price): 
                    btc = get_balance("BTC")
                    if btc > 0.00008:
                        upbit.sell_market_order(ticker, btc*0.9995)
                    state = 0
                elif (current_price < lower_price):
                    buy_price = current_price
                    buy_hour = now.hour
                    buy_minute = now.minute
                    state = 1
            else:
                buy_price = current_price
                buy_hour = now.hour
                buy_minute = now.minute
                state = 1
            
            if (current_price < close_min):
                btc = get_balance("BTC")
                if btc > 0.00008:
                    upbit.sell_market_order(ticker, btc*0.9995)
                state = 0
                
        # Print
        iii = min(10, iii + 1)
        print("autotrade running", iii, '/ state: ', state)
        print(now.hour,'/',now.minute,'/',now.second)
        print(get_balance("BTC"))
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
