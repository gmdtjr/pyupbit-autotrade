from dataclasses import asdict
from os import lseek
import time
import pyupbit
import datetime
import numpy as np
import math
from time import sleep

minute_interval = 1

def get_current_price(ticker, load_day):
    #"""Current Price Check"""
    while(1):
        df_m = pyupbit.get_ohlcv(ticker, interval="minute1", count = 1, to=load_day) ## 1분 단위
        if (not df_m is None):
            break

    if (not df_m is None):
        current_price = float(df_m['open']) ## 2021 01 01 9:00 ~ 2021 01 02 8:59
    else:
        current_price = 0
        print('fail')
    
    return current_price

def buy_val_update(ticker, load_day):

    gain = 100

    # Data Loading
    for i in range(1,10):
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count = 2, to=load_day)
        if (not df is None):
            break

    if (not df is None):
        # Mean Price 
        value = float(df['value'][0])/60
        buy_val = round(value/gain, -2)
        if (buy_val < 10000):
            buy_val = 0
    else:
        buy_val = 0

    return buy_val

def strategy(ticker, cp, state, close, range_val, pattern, buy_val, bp, tp_range, cash, btc):

    k = 0.5

    if (state == 0 and cp <= close - k*(range_val) and pattern == 2 and buy_val > 0):
        buy_val = min(buy_val, 1000000)
        krw = buy_val
        btc = btc + (0.9995*krw/cp) 
        cash = cash - krw

        state = 1
        bp = cp
        tp_range = k*(range_val)
        
    elif (state == 1):
        target_high = bp + 2*tp_range
        target_low = bp - 2*tp_range

        if (cp >= target_high):
            cash = cash + (0.9995*btc*cp) 
            btc = 0
            state = 0

        if (cp <= target_low):
            bp = cp
            tp_range = 0.8*tp_range

    return state, bp, tp_range, cash, btc


# Simulation Time 
class Time: 
    year: int = None
    month: int = None
    day: int = None
    hour: int = None
    minute: int = None
    second: int = None

now = Time()

now.year = 2022
now.month = 2
now.day = 28
now.hour = 23
now.minute = 59

cash = 20000000
btc = 0
# Initial flag setting
coin_list = pyupbit.get_tickers(fiat="KRW")
coin_num = len(coin_list)
ticker_list = coin_list
valid = np.zeros(coin_num)
state = np.zeros(coin_num)
bp = np.zeros(coin_num)
cp = np.zeros(coin_num)
tp_range = np.zeros(coin_num)
high = np.zeros(coin_num)
low = np.zeros(coin_num)
high_t = np.zeros(coin_num)
low_t = np.zeros(coin_num)
update_flag = np.zeros(coin_num)
close = np.zeros(coin_num)
range_val = np.zeros(coin_num)
range_pattern = np.zeros(coin_num)
buy_val = np.zeros(coin_num)
kkk = np.zeros(coin_num)
btc = np.zeros(coin_num)

day_pre = now.day
ini_flag = 0
print("Sim Start")
while (not (now.year == 2022 and now.month == 3 and now.day == 18)):
#for iii in range(3):
#while (0):

    ## Time Update
    now.minute = now.minute + minute_interval
    if (now.minute >= 60):
        now.minute = 0
        now.hour = now.hour + 1
    if (now.hour >= 24):
        now.hour = 0
        now.day = now.day + 1
        if (now.month == 1 or now.month == 3 or now.month == 5 or now.month == 7 or now.month == 8 or now.month == 10 or now.month == 12):
            if (now.day > 31):
                now.day = 1
                now.month = now.month + 1
                if (now.month == 13):  ## 윤달은 나중에 고려 어차피 2023년
                    now.month = 1
                    now.year = now.year + 1
        if (now.month == 4 or now.month == 6 or now.month == 9 or now.month == 11):
            if (now.day > 30):
                now.day = 1
                now.month = now.month + 1
        if (now.month == 2):
            if (now.day > 28):
                now.day = 1
                now.month = now.month + 1

    ## Load Day
    if (now.month <= 9):
        load_day = str(now.year) + '0' + str(now.month)
    else:
        load_day = str(now.year) + str(now.month)

    if (now.day <= 9):
        load_day = load_day + '0' + str(now.day)
    else:
        load_day = load_day + str(now.day)

    load_day = load_day + ' '

    if (now.hour <= 9):
        load_day = load_day + '0' + str(now.hour)
    else:
        load_day = load_day + str(now.hour)

    load_day = load_day + ':'

    if (now.minute <= 9):
        load_day = load_day + '0' + str(now.minute)
    else:
        load_day = load_day + str(now.minute)

    load_day = load_day + ':00'

    if (now.hour >= 23):
        ini_flag = 0

    if (now.day != day_pre and ini_flag == 0):
        # Valid Update
        for i in range(1,len(coin_list)):
            for j in range(1,10):
                sleep(0.1)
                df = pyupbit.get_ohlcv(coin_list[i-1], interval="day", count = 2, to=load_day)
                if (not df is None):
                    break
            if (not df is None):
                if (state[i-1] == 0):
                    if (df['value'][0]/(24*60) > 10000000):
                        valid[i-1] = 1
                    else:
                        valid[i-1] = 0
                        kkk[i-1] = 0
        ini_flag = 1

    ## Current price update
    for i in range(1,coin_num+1):
        if (valid[i-1] == 1):
            sleep(0.1)
            cp[i-1] = get_current_price(ticker_list[i-1], load_day)

    ## Range update
    for i in range(1,coin_num+1):
        if (valid[i-1] == 1):
            if (update_flag[i-1] == 0 and now.minute == 0):    
                low[i-1] = cp[i-1]
                high[i-1] = cp[i-1]
                low_t[i-1] = 0
                high_t[i-1] = 0
                update_flag[i-1] = 1

                sleep(0.1)
                buy_val[i-1] = buy_val_update(ticker_list[i-1], load_day)
            elif (update_flag[i-1] == 1):
                
                if (high[i-1] <= cp[i-1]):
                    high[i-1] = cp[i-1]
                    high_t[i-1] = now.minute

                if (low[i-1] >= cp[i-1]):
                    low[i-1] = cp[i-1]
                    low_t[i-1] = now.minute

                if (now.minute >= 59):
                    close[i-1] = cp[i-1]
                    if (low_t[i-1] <= high_t[i-1]):
                        range_pattern[i-1] = 1
                    else:
                        range_pattern[i-1] = 2
                    range_val[i-1] = high[i-1] - low[i-1]
                    update_flag[i-1] = 0
                    kkk[i-1] = kkk[i-1] + 1

    # Strategy Planning
    for i in range(1,coin_num+1):
        if (valid[i-1] == 1 and kkk[i-1] > 0):
            state[i-1], bp[i-1], tp_range[i-1], cash, btc[i-1] = strategy(ticker_list[i-1], cp[i-1], state[i-1], close[i-1], range_val[i-1], range_pattern[i-1], buy_val[i-1], bp[i-1], tp_range[i-1], cash, btc[i-1])
        
    # State Sum
    state_sum = 0
    for i in range(1,coin_num+1):
        state_sum = state_sum + state[i-1]
    valid_sum = 0
    for i in range(1,coin_num+1):
        valid_sum = valid_sum + valid[i-1]
    cash_temp = 0
    for i in range(1,coin_num+1):
        cash_temp = cash_temp + btc[i-1]*cp[i-1]
    buy_val_sum = 0
    for i in range(1,coin_num+1):
        if (state[i-1] == 1):
            buy_val_sum = buy_val_sum + buy_val[i-1]
    # Time Feedback
    day_pre = now.day
    # Print
    print('Now Time:', now.month, '.', now.day, '.', now.hour, '.', now.minute, ',', now.second,'/ cash:', cash + cash_temp)
    print('state sum:', state_sum, '/ valid num:', valid_sum, '/ coin num:', coin_num, '/ buy val sum:', buy_val_sum)
    print('state:', state[0], '/ cp:', cp[0], '/ buy val:', buy_val[0], '/ range val:', range_val[0])
    print('---------------------------------')
    time.sleep(1)

