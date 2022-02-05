from dataclasses import asdict
from os import lseek
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

def strategy(ticker, tic, kkk, hhh, state, buy_price, ratio):

    current_price = get_current_price(ticker)

    # Data Loading
    df = pyupbit.get_ohlcv(ticker, interval="minute60", count = 25)
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
     
    # Buy Strategy
    if (state == 0 and hhh >= 3):
        if (current_price < low_1 and current_price < low_mean and current_price > high_min):
            krw = (get_balance("KRW"))
            krw = ratio*krw
            if krw > 5000:
                upbit.buy_market_order(ticker, krw*0.9995)
            state = 1
            buy_price = current_price
            kkk = 0

    # Sell Strategy
    if (state == 1):
        if (kkk <= 360): ## 1시간 경과
            percent = 0.015 - 0.015*(kkk/360)
            target_price = buy_price*(1+percent)
            percent = 0.01 - 0.01*(kkk/360)
            lower_price = buy_price*(1-percent)
            if (current_price >= target_price): 
                btc = get_balance(tic)
                if btc > 0:
                    upbit.sell_market_order(ticker, btc*0.9995)
                state = 0
                kkk = 0
                hhh = 0
            elif (current_price <= lower_price):
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
            state = 0
            kkk = 0
            hhh = 0

    return kkk, hhh, state, buy_price, current_price, low_mean, high_min, low_min

# Log-In
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# Initial flag setting
coin_num = 15
ticker_list = ["KRW-BTC", "KRW-ETH", "KRW-STRK", "KRW-HUNT", "KRW-JST", "KRW-BORA", "KRW-XRP", "KRW-SAND", "KRW-SOL", "KRW-ONT", "KRW-LSK", "KRW-MANA", "KRW-NEAR", "KRW-AXS", "KRW-GAS"]
tic_list = ["BTC", "ETH", "STRK", "HUNT", "JST", "BORA", "XRP", "SAND", "SOL", "ONT", "LSK", "MANA", "NEAR", "AXS", "GAS"]
ratio = 0.5
state = np.zeros(coin_num)
buy_price = np.zeros(coin_num)
kkk = np.zeros(coin_num)
current_price = np.zeros(coin_num)
low_mean = np.zeros(coin_num)
high_min = np.zeros(coin_num)
low_min = np.zeros(coin_num)
hhh = 3*np.ones(coin_num)

now = datetime.datetime.now()
print(now.hour, now.minute, 30%24)

minute_pre = now.minute
hour_pre = now.hour
# Autotrading Start
while True:
    try:
        # Time Update
        now = datetime.datetime.now()
        schedule.run_pending()

        if (now.minute != minute_pre):
            for i in range(1,coin_num+1):
                kkk[i-1] = kkk[i-1] + 1
        if (now.hour != hour_pre):
            for i in range(1,coin_num+1):
                hhh[i-1] = hhh[i-1] + 1
           
        for i in range(1,coin_num+1):
            kkk[i-1], hhh[i-1], state[i-1], buy_price[i-1], current_price[i-1], low_mean[i-1], high_min[i-1], low_min[i-1] = strategy(ticker_list[i-1], tic_list[i-1], kkk[i-1], hhh[i-1], state[i-1], buy_price[i-1], ratio)

        minute_pre = now.minute
        hour_pre = now.hour
        
        # Print
        print(now.hour,'/',now.minute,'/',now.second)
        for i in range(1,coin_num+1):
            print(tic_list[i-1],'-','st:',state[i-1],'/k:',kkk[i-1],'/h:',hhh[i-1],'/bp:',buy_price[i-1],'/cp:',current_price[i-1],'/mp:',round(low_mean[i-1],1),'/hp:',high_min[i-1],'/lp:',low_min[i-1])
        
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)