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

# Initial flag setting
ticker_A = "KRW-BTC"
ticker_B = "KRW-ETH"
ticker_C = "KRW-STRK"
tic_A = "BTC"
tic_B = "ETH"
tic_C = "STRK"
state_A = 0
state_B = 0 
state_C = 0 
buy_price_A = 0
buy_price_B = 0
buy_price_C = 0
target_price = 0.0
lower_price = 0.0
kkk_A = 0
kkk_B = 0
kkk_C = 0

now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

minute_pre = now.minute
# Autotrading Start
while True:
    try:
        # Time Update
        now = datetime.datetime.now()
        if (now.minute != minute_pre):
            kkk_A = kkk_A + 1
            kkk_B = kkk_B + 1
            kkk_C = kkk_C + 1
        schedule.run_pending()
        current_price_A = get_current_price(ticker_A)
        current_price_B = get_current_price(ticker_B)
        current_price_C = get_current_price(ticker_C)

        # Data Loading
        df_A = pyupbit.get_ohlcv("KRW-BTC", interval="minute60", count = 30)
        df_B = pyupbit.get_ohlcv("KRW-ETH", interval="minute60", count = 30)
        df_C = pyupbit.get_ohlcv("KRW-STRK", interval="minute60", count = 30)
        # Mean Price 
        low_1_A = float(df_A['low'][-2:-1])
        low_2_A = float(df_A['low'][-3:-2])
        low_3_A = float(df_A['low'][-4:-3])
        low_mean_A = (low_1_A + low_2_A + low_3_A)/3

        
        low_1_B = float(df_B['low'][-2:-1])
        low_2_B = float(df_B['low'][-3:-2])
        low_3_B = float(df_B['low'][-4:-3])
        low_mean_B = (low_1_B + low_2_B + low_3_B)/3

        low_1_C = float(df_C['low'][-2:-1])
        low_2_C = float(df_C['low'][-3:-2])
        low_3_C = float(df_C['low'][-4:-3])
        low_mean_C = (low_1_C + low_2_C + low_3_C)/3

        # High Low Price 
        high_min_A = 999999999999999
        low_min_A = 999999999999999
        for i in range(-24,0):
            high_temp = float(df_A['high'][-1+i:0+i])
            if (high_min_A > high_temp):
                high_min_A = high_temp     
        for i in range(-24,0):
            low_temp = float(df_A['low'][-1+i:0+i])
            if (low_min_A > low_temp):
                low_min_A = low_temp         

        high_min_B = 999999999999999
        low_min_B = 999999999999999
        for i in range(-24,0):
            high_temp = float(df_B['high'][-1+i:0+i])
            if (high_min_B > high_temp):
                high_min_B = high_temp     
        for i in range(-24,0):
            low_temp = float(df_B['low'][-1+i:0+i])
            if (low_min_B > low_temp):
                low_min_B = low_temp      

        high_min_C = 999999999999999
        low_min_C = 999999999999999
        for i in range(-24,0):
            high_temp = float(df_C['high'][-1+i:0+i])
            if (high_min_C > high_temp):
                high_min_C = high_temp     
        for i in range(-24,0):
            low_temp = float(df_C['low'][-1+i:0+i])
            if (low_min_C > low_temp):
                low_min_C = low_temp           

        # Buy Strategy - HUNT
        if (state_A == 0):
            if (current_price_A < low_mean_A and current_price_A > high_min_A):
                krw = (get_balance("KRW"))
                if krw > 5000:
                    upbit.buy_market_order(ticker_A, krw*0.9995)
                    state_A = 1
                buy_price_A = current_price_A
                kkk_A = 0

        # Buy Strategy - STRK
        if (state_B == 0):
            if (current_price_B < low_mean_B and current_price_B > high_min_B):
                krw = (get_balance("KRW"))
                if krw > 5000:
                    upbit.buy_market_order(ticker_B, krw*0.9995)
                    state_B = 1
                buy_price_B = current_price_B
                kkk_B = 0

        # Buy Strategy - STRK
        if (state_C == 0):
            if (current_price_C < low_mean_C and current_price_C > high_min_C):
                krw = (get_balance("KRW"))
                if krw > 5000:
                    upbit.buy_market_order(ticker_C, krw*0.9995)
                    state_C = 1
                buy_price_C = current_price_C
                kkk_C = 0

        # Sell Strategy - HUNT
        if (state_A == 1):
            if (kkk_A <= 360): ## 1시간 경과
                percent = 0.015 - 0.015*(kkk_A/360)
                target_price = buy_price_A*(1+percent)
                percent = 0.01 - 0.01*(kkk_A/360)
                lower_price = buy_price_A*(1-percent)
                if (current_price_A > target_price): 
                    btc = get_balance(tic_A)
                    if btc > 0:
                        upbit.sell_market_order(ticker_A, btc*0.9995)
                    state_A = 0
                    kkk_A = 0
                elif (current_price_A < lower_price):
                    buy_price_A = current_price_A
                    state_A = 1
            else:
                buy_price_A = current_price_A
                state_A = 1
                kkk_A = 360
            
            if (current_price_A < low_min_A):
                btc = get_balance(tic_A)
                if btc > 0:
                    upbit.sell_market_order(ticker_A, btc*0.9995)
                state_A = 0
                kkk_A = 0

        # Sell Strategy - STRK
        if (state_B == 1):
            if (kkk_B <= 360): ## 1시간 경과
                percent = 0.015 - 0.015*(kkk_B/360)
                target_price = buy_price_B*(1+percent)
                percent = 0.01 - 0.01*(kkk_B/360)
                lower_price = buy_price_B*(1-percent)
                if (current_price_B > target_price): 
                    btc = get_balance(tic_B)
                    if btc > 0:
                        upbit.sell_market_order(ticker_B, btc*0.9995)
                    state_B = 0
                    kkk_B = 0
                elif (current_price_B < lower_price):
                    buy_price_B = current_price_B
                    state_B = 1
            else:
                buy_price_B = current_price_B
                state_B = 1
                kkk_B = 360
            
            if (current_price_B < low_min_B):
                btc = get_balance(tic_B)
                if btc > 0:
                    upbit.sell_market_order(ticker_B, btc*0.9995)
                state_B = 0
                kkk_B = 0

        # Sell Strategy - STRK
        if (state_C == 1):
            if (kkk_C <= 360): ## 1시간 경과
                percent = 0.015 - 0.015*(kkk_C/360)
                target_price = buy_price_C*(1+percent)
                percent = 0.01 - 0.01*(kkk_C/360)
                lower_price = buy_price_C*(1-percent)
                if (current_price_C > target_price): 
                    btc = get_balance(tic_C)
                    if btc > 0:
                        upbit.sell_market_order(ticker_C, btc*0.9995)
                    state_C = 0
                    kkk_C = 0
                elif (current_price_C < lower_price):
                    buy_price_C = current_price_C
                    state_C = 1
            else:
                buy_price_C = current_price_C
                state_C = 1
                kkk_C = 360
            
            if (current_price_C < low_min_C):
                btc = get_balance(tic_C)
                if btc > 0:
                    upbit.sell_market_order(ticker_C, btc*0.9995)
                state_C = 0
                kkk_C = 0

        minute_pre = now.minute
        # Print
        print(now.hour,'/',now.minute,'/',now.second)
        print('BTC-','st:',state_A,'/k:',kkk_A,'/bp:',buy_price_A,'/current:',current_price_A,'/mean:',round(low_mean_A,1),'/low:',low_min_A,'/high:',high_min_A)
        print('ETH-','st:',state_B,'/k:',kkk_B,'/bp:',buy_price_B,'/current:',current_price_B,'/mean:',round(low_mean_B,1),'/low:',low_min_B,'/high:',high_min_B)
        print('STRK-','st:',state_C,'/k:',kkk_C,'/bp:',buy_price_C,'/current:',current_price_C,'/mean:',round(low_mean_C,1),'/low:',low_min_C,'/high:',high_min_C)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)