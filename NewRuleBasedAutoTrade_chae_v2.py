from dataclasses import asdict
import time
import pyupbit
import datetime
import schedule
import numpy as np
import math

access = "ErGOGkF8IxVzxyVQNTwVJ0dyAkElQKrB9aT6Hfle"          
secret = "uK8ZXHoUkXmiKEXxZ8YlHm7IeNfKRwml4i6NrPs8"          

def get_balance(ticker):
    #"""Balance Chech"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    #"""Current Price Check"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# Log-In
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# Data Loading
df_X = pyupbit.get_ohlcv("KRW-HUNT", interval="minute60", count = 50)
ticker_X = "KRW-HUNT"
df_S = pyupbit.get_ohlcv("KRW-STRK", interval="minute60", count = 50)
ticker_S = "KRW-STRK"
# Initial flag setting
state_X = 0
state_S = 0 
buy_price_X = 0
buy_price_S = 0
target_price = 0.0
lower_price = 0.0
kkk_X = 0
kkk_S = 0

now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

minute_pre = now.minute
# Autotrading Start
while True:
    try:
        # Time Update
        now = datetime.datetime.now()
        if (now.minute != minute_pre):
            kkk_X = kkk_X + 1
            kkk_S = kkk_S + 1
        schedule.run_pending()
        current_price_X = get_current_price(ticker_X)
        current_price_S = get_current_price(ticker_S)

        # Mean Price 
        low_1_X = float(df_X['low'][-2:-1])
        low_2_X = float(df_X['low'][-3:-2])
        low_3_X = float(df_X['low'][-4:-3])
        low_mean_X = (low_1_X + low_2_X + low_3_X)/3

        low_1_S = float(df_S['low'][-2:-1])
        low_2_S = float(df_S['low'][-3:-2])
        low_3_S = float(df_S['low'][-4:-3])
        low_mean_S = (low_1_S + low_2_S + low_3_S)/3

        # High Low Price 
        high_min_X = 999999999999999
        low_min_X = 999999999999999
        for i in range(-24,0):
            high_temp = float(df_X['high'][-1+i:0+i])
            if (high_min_X > high_temp):
                high_min_X = high_temp     
        for i in range(-24,0):
            low_temp = float(df_X['low'][-1+i:0+i])
            if (low_min_X > low_temp):
                low_min_X = low_temp         

        high_min_S = 999999999999999
        low_min_S = 999999999999999
        for i in range(-24,0):
            high_temp = float(df_S['high'][-1+i:0+i])
            if (high_min_S > high_temp):
                high_min_S = high_temp     
        for i in range(-24,0):
            low_temp = float(df_S['low'][-1+i:0+i])
            if (low_min_S > low_temp):
                low_min_S = low_temp         

        # Buy Strategy - STRK
        if (state_S == 0):
            if (current_price_S < low_mean_S and current_price_S > high_min_S):
                if (state_X == 0):
                    krw = 0.5*(get_balance("KRW"))
                    if krw > 5000:
                        upbit.buy_market_order(ticker_S, krw*0.9995)
                        state_S = 1
                    buy_price_S = current_price_S
                    kkk_S = 0
                else:
                    krw = (get_balance("KRW"))
                    if krw > 5000:
                        upbit.buy_market_order(ticker_S, krw*0.9995)
                        state_S = 1
                    buy_price_S = current_price_S
                    kkk_S = 0

        # Buy Strategy - XRP
        if (state_X == 0):
            if (current_price_X < low_mean_X and current_price_X > high_min_X):
                if (state_S == 0):
                    krw = 0.5*(get_balance("KRW"))
                    if krw > 5000:
                        upbit.buy_market_order(ticker_X, krw*0.9995)
                        state_X = 1
                    buy_price_X = current_price_X
                    kkk_X = 0
                else:
                    krw = (get_balance("KRW"))
                    if krw > 5000:
                        upbit.buy_market_order(ticker_X, krw*0.9995)
                        state_X = 1
                    buy_price_X = current_price_X
                    kkk_X = 0

        # Sell Strategy - STRK
        if (state_S == 1):
            if (kkk_S <= 360): ## 1시간 경과
                percent = 0.015 - 0.015*(kkk_S/360)
                target_price = buy_price_S*(1+percent)
                percent = 0.01 - 0.01*(kkk_S/360)
                lower_price = buy_price_S*(1-percent)
                if (current_price_S > target_price): 
                    btc = get_balance("STRK")
                    if btc > 0:
                        upbit.sell_market_order(ticker_S, btc*0.9995)
                    state_S = 0
                    kkk_S = 0
                elif (current_price_S < lower_price):
                    buy_price_S = current_price_S
                    state_S = 1
            else:
                buy_price_S = current_price_S
                state_S = 1
                kkk_S = 360
            
            if (current_price_S < low_min_S):
                btc = get_balance("STRK")
                if btc > 0:
                    upbit.sell_market_order(ticker_S, btc*0.9995)
                state_S = 0
                kkk_S = 0

        # Sell Strategy - HUNT
        if (state_X == 1):
            if (kkk_X <= 360): ## 1시간 경과
                percent = 0.015 - 0.015*(kkk_X/360)
                target_price = buy_price_X*(1+percent)
                percent = 0.01 - 0.01*(kkk_X/360)
                lower_price = buy_price_X*(1-percent)
                if (current_price_X > target_price): 
                    btc = get_balance("HUNT")
                    if btc > 0:
                        upbit.sell_market_order(ticker_X, btc*0.9995)
                    state_X = 0
                    kkk_X = 0
                elif (current_price_X < lower_price):
                    buy_price_X = current_price_X
                    state_X = 1
            else:
                buy_price_X = current_price_X
                state_X = 1
                kkk_X = 360
            
            if (current_price_X < low_min_X):
                btc = get_balance("HUNT")
                if btc > 0:
                    upbit.sell_market_order(ticker_X, btc*0.9995)
                state_X = 0
                kkk_X = 0

        minute_pre = now.minute
        # Print
        print(now.hour,'/',now.minute,'/',now.second)
        print('STRK-','st:',state_S,'/k:',kkk_S,'/bp:',buy_price_S,'/current:',current_price_S,'/mean:',round(low_mean_S,1),'/low:',low_min_S,'/high:',high_min_S)
        print('HUNT-','st:',state_X,'/k:',kkk_X,'/bp:',buy_price_X,'/current:',current_price_X,'/mean:',round(low_mean_X,1),'/low:',low_min_X,'/high:',high_min_X)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)