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

def strategy(ticker, tic, kkk, state, buy_price, ratio):

    current_price = get_current_price(ticker)

    # Data Loading
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count = 30)
    # Mean Price 
    low_1 = float(df['low'][-2:-1])
    low_2 = float(df['low'][-3:-2])
    low_3 = float(df['low'][-4:-3])
    low_mean = (low_1 + low_2 + low_3)/3

    # High Low Price 
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
     
    # Buy Strategy - HUNT
    if (state == 0):
        if (current_price < low_mean and current_price > high_min):
            krw = (get_balance("KRW"))
            krw = ratio*krw
            if krw > 5000:
                upbit.buy_market_order(ticker, krw*0.9995)
                state = 1
            buy_price = current_price
            kkk = 0

    # Sell Strategy - HUNT
    if (state == 1):
        if (kkk <= 360): ## 1시간 경과
            percent = 0.015 - 0.015*(kkk/360)
            target_price = buy_price*(1+percent)
            percent = 0.01 - 0.01*(kkk/360)
            lower_price = buy_price*(1-percent)
            if (current_price > target_price): 
                if (not (current_price < low_mean and current_price > high_min)):
                    btc = get_balance(tic)
                    if btc > 0:
                        upbit.sell_market_order(ticker, btc*0.9995)
                        1
                    state = 0
                    kkk = 0
                else:
                    buy_price = current_price
                    state = 1
                    kkk = 0
            elif (current_price < lower_price):
                buy_price = current_price
                state = 1
        else:
            buy_price = current_price
            state = 1
            kkk = 360
        
        if (current_price < low_min):
            btc = get_balance(tic)
            if btc > 0:
                upbit.sell_market_order(ticker, btc*0.9995)
                1
            state = 0
            kkk = 0

    return kkk, state, buy_price

# Log-In
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# Initial flag setting
ticker_1 = "KRW-BTC"
ticker_2 = "KRW-ETH"
ticker_3 = "KRW-STRK"
ticker_4 = "KRW-HUNT"
ticker_5 = "KRW-JST"
ticker_6 = "KRW-BORA"
ticker_7 = "KRW-XRP"
ticker_8 = "KRW-SAND"
ticker_9 = "KRW-SOL"
ticker_10 = "KRW-ONT"
tic_1 = "BTC"
tic_2 = "ETH"
tic_3 = "STRK"
tic_4 = "HUNT"
tic_5 = "JST"
tic_6 = "BORA"
tic_7 = "XRP"
tic_8 = "SAND"
tic_9 = "SOL"
tic_10 = "ONT"
ratio_1 = 0.9
ratio_2 = 0.6
ratio_3 = 0.3
ratio_4 = 0.2
ratio_5 = 0.4
ratio_6 = 0.2
ratio_7 = 0.2
ratio_8 = 0.3
ratio_9 = 0.3
ratio_10 = 0.2
state_1 = 0
state_2 = 0 
state_3 = 0 
state_4 = 0
state_5 = 0 
state_6 = 0 
state_7 = 0
state_8 = 0 
state_9 = 0 
state_10 = 0
buy_price_1 = 0
buy_price_2 = 0
buy_price_3 = 0
buy_price_4 = 0
buy_price_5 = 0
buy_price_6 = 0
buy_price_7 = 0
buy_price_8 = 0
buy_price_9 = 0
buy_price_10 = 0
kkk_1 = 0
kkk_2 = 0
kkk_3 = 0
kkk_4 = 0
kkk_5 = 0
kkk_6 = 0
kkk_7 = 0
kkk_8 = 0
kkk_9 = 0
kkk_10 = 0

now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

minute_pre = now.minute
# Autotrading Start
while True:
    try:
        # Time Update
        now = datetime.datetime.now()
        schedule.run_pending()

        if (now.minute != minute_pre):
            kkk_1 = kkk_1 + 1
            kkk_2 = kkk_2 + 1
            kkk_3 = kkk_3 + 1
            kkk_4 = kkk_4 + 1
            kkk_5 = kkk_5 + 1
            kkk_6 = kkk_6 + 1
            kkk_7 = kkk_7 + 1
            kkk_8 = kkk_8 + 1
            kkk_9 = kkk_9 + 1
            kkk_10 = kkk_10 + 1
           
        kkk_1, state_1, buy_price_1 = strategy(ticker_1, tic_1, kkk_1, state_1, buy_price_1, ratio_1)
        kkk_2, state_2, buy_price_2 = strategy(ticker_2, tic_2, kkk_2, state_2, buy_price_2, ratio_2)
        kkk_3, state_3, buy_price_3 = strategy(ticker_3, tic_3, kkk_3, state_3, buy_price_3, ratio_3)
        kkk_4, state_4, buy_price_4 = strategy(ticker_4, tic_4, kkk_4, state_4, buy_price_4, ratio_4)
        kkk_5, state_5, buy_price_5 = strategy(ticker_5, tic_5, kkk_5, state_5, buy_price_5, ratio_5)
        kkk_6, state_6, buy_price_6 = strategy(ticker_6, tic_6, kkk_6, state_6, buy_price_6, ratio_6)
        kkk_7, state_7, buy_price_7 = strategy(ticker_7, tic_7, kkk_7, state_7, buy_price_7, ratio_7)
        kkk_8, state_8, buy_price_8 = strategy(ticker_8, tic_8, kkk_8, state_8, buy_price_8, ratio_8)
        kkk_9, state_9, buy_price_9 = strategy(ticker_9, tic_9, kkk_9, state_9, buy_price_9, ratio_9)
        kkk_10, state_10, buy_price_10 = strategy(ticker_10, tic_10, kkk_10, state_10, buy_price_10, ratio_10)

        minute_pre = now.minute
        # Print
        print(now.hour,'/',now.minute,'/',now.second)
        print(tic_1,'-','st:',state_1,'/k:',kkk_1,'/bp:',buy_price_1)
        print(tic_2,'-','st:',state_2,'/k:',kkk_2,'/bp:',buy_price_2)
        print(tic_3,'-','st:',state_3,'/k:',kkk_3,'/bp:',buy_price_3)
        print(tic_4,'-','st:',state_4,'/k:',kkk_4,'/bp:',buy_price_4)
        print(tic_5,'-','st:',state_5,'/k:',kkk_5,'/bp:',buy_price_5)
        print(tic_6,'-','st:',state_6,'/k:',kkk_6,'/bp:',buy_price_6)
        print(tic_7,'-','st:',state_7,'/k:',kkk_7,'/bp:',buy_price_7)
        print(tic_8,'-','st:',state_8,'/k:',kkk_8,'/bp:',buy_price_8)
        print(tic_9,'-','st:',state_9,'/k:',kkk_9,'/bp:',buy_price_9)
        print(tic_10,'-','st:',state_10,'/k:',kkk_10,'/bp:',buy_price_10)
        
        #print('BTC-','st:',state_A,'/k:',kkk_A,'/bp:',buy_price_A,'/current:',current_price_A,'/mean:',round(low_mean_A,1),'/low:',low_min_A,'/high:',high_min_A)
        #print('ETH-','st:',state_B,'/k:',kkk_B,'/bp:',buy_price_B,'/current:',current_price_B,'/mean:',round(low_mean_B,1),'/low:',low_min_B,'/high:',high_min_B)
        #print('STRK-','st:',state_C,'/k:',kkk_C,'/bp:',buy_price_C,'/current:',current_price_C,'/mean:',round(low_mean_C,1),'/low:',low_min_C,'/high:',high_min_C)

        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)