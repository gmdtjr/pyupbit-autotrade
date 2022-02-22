# 현재 돌리고 있는 코드, 2021.11부터 5분 간격, no ratio
from dataclasses import asdict
from os import lseek
import time
import pyupbit
import datetime
import numpy as np
import math

minute_interval = 1
def get_current_price(ticker, load_day):
    #"""Current Price Check"""
    for i in range(1,5):
        df_m = pyupbit.get_ohlcv(ticker, interval="minute1", count = 1, to=load_day) ## 1분 단위
        if (not df_m is None):
            break

    if (not df_m is None):
        current_price = float(df_m['close']) ## 2021 01 01 9:00 ~ 2021 01 02 8:59
    else:
        current_price = 0
        print('fail')
    
    return current_price

def update_1hour(ticker, load_day):

    # Data Loading
    for i in range(1,5):
        df = pyupbit.get_ohlcv(ticker, interval="minute60", count = 25, to=load_day) ## 1시간 단위  
        if (not df is None):
            break
    
    if (not df is None):
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
    else:
        low_mean = 0
        high_min = 0
        low_min = 0
        low_1 = 0
        low_2 = 0
        low_3 = 0
        print('fail2')

    return low_mean, high_min, low_min
     

def strategy(ticker, kkk, hhh, state, buy_price, low_mean, high_min, low_min, load_day, cash, btc, buy_price_origin, stop_flag):

    current_price = get_current_price(ticker, load_day)
    
    # Buy Strategy
    if (state == 0 and hhh >= 1 and stop_flag == 0):
        if (current_price < low_mean and current_price > high_min):
            if cash > 105000:
                krw = 100000
                btc = btc + (0.9995*krw/current_price) 
                cash = cash - krw
            elif cash <= 105000 and cash > 10000:
                krw = cash
                btc = btc + (0.9995*krw/current_price) 
                cash = cash - krw
            state = 1
            buy_price = current_price
            buy_price_origin = current_price
            kkk = 0

    # Sell Strategy
    if (state == 1):
        if (kkk <= 360): ## 1시간 경과
            percent = 0.015 - 0.015*(kkk/360)
            target_price = buy_price*(1+percent)
            percent = 0.01 - 0.01*(kkk/360)
            lower_price = buy_price*(1-percent)
            if (current_price >= target_price): 
                cash = cash + (0.9995*btc*current_price) 
                btc = 0
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
            cash = cash + (0.9995*btc*current_price) 
            btc = 0
            state = 0
            kkk = 0
            hhh = 0

        if (stop_flag == 1):
            cash = cash + (0.9995*btc*current_price) 
            btc = 0

    # Rate Calculation
    if (state == 1):
        rate = 100*(current_price - buy_price_origin)/buy_price_origin
        # if (rate_temp > 0):
        #     rate = 1
        # elif (rate_temp < 0):
        #     rate = -1
        # else:
        #     rate = 0
    else:
        rate = 0

    return kkk, hhh, state, buy_price, current_price, cash, btc, buy_price_origin, rate

# Initial flag setting

# Simulation Time 
class Time: 
    year: int = None
    month: int = None
    day: int = None
    hour: int = None
    minute: int = None

now = Time()

now.year = 2022
now.month = 2
now.day = 1
now.hour = 0
now.minute = 0

minute_pre = now.minute
hour_pre = now.hour
day_pre = now.day

cash = 2000000
cash_virtual = cash
state_sum = 0
update_flag = 0
ini_flag = 0

# Autotrading Start
print("Sim Start")
while (not (now.year == 2022 and now.month == 2 and now.day == 15)):

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

    # Initialize
    if (state_sum == 0 and ini_flag == 0):
        coin_list = pyupbit.get_tickers(fiat="KRW")
        coin_list_valid = []
        for i in range(1,len(coin_list)):

            for j in range(1,5):
                df_m = pyupbit.get_ohlcv(coin_list[i-1], interval="day", count = 2, to = load_day)
                if (not df_m is None):
                    break
            if (not df_m is None):
                if (float(df_m['value'][0])/(24*60) > 5000000 and float(df_m['close'][0]) > 100):
                    coin_list_valid.append(coin_list[i-1])

        coin_num = len(coin_list_valid)
        ticker_list = coin_list_valid
        state = np.zeros(coin_num)
        buy_price = np.zeros(coin_num)
        kkk = np.zeros(coin_num)
        current_price = np.zeros(coin_num)
        low_mean = np.zeros(coin_num)
        high_min = np.zeros(coin_num)
        low_min = np.zeros(coin_num)
        hhh = np.ones(coin_num)
        btc = np.zeros(coin_num)
        buy_price_origin = np.zeros(coin_num)
        rate = np.zeros(coin_num)
        rate_sum = 0
        for i in range(1,coin_num+1):
            low_mean[i-1], high_min[i-1], low_min[i-1] = update_1hour(ticker_list[i-1], load_day)
        update_flag = 1
        ini_flag = 1
        print("Initializing: ", now.hour,'/',now.minute)

    if (state_sum == 0):
        rate_accu = 0
        cash_virtual = cash
        stop_flag = 0

    # Time Update
    if (now.minute != minute_pre):
        for i in range(1,coin_num+1):
            kkk[i-1] = kkk[i-1] + minute_interval
    if (now.hour != hour_pre):
        for i in range(1,coin_num+1):
            hhh[i-1] = hhh[i-1] + 1
    if (now.day != day_pre):
        ini_flag = 0

    if (now.minute <= 30 and update_flag == 0):
        for i in range(1,coin_num+1):
            low_mean[i-1], high_min[i-1], low_min[i-1] = update_1hour(ticker_list[i-1], load_day)
        update_flag = 1
    elif (now.minute <= 30 and update_flag == 1):
        update_flag = 1
    else:
        update_flag = 0
    
    for i in range(1,coin_num+1):
        time.sleep(0.1)
        kkk[i-1], hhh[i-1], state[i-1], buy_price[i-1], current_price[i-1], cash, btc[i-1], buy_price_origin[i-1], rate[i-1] = strategy(ticker_list[i-1], kkk[i-1], hhh[i-1], state[i-1], buy_price[i-1], low_mean[i-1], high_min[i-1], low_min[i-1], load_day, cash, btc[i-1], buy_price_origin[i-1], stop_flag)

    rate_sum_temp = 0    
    for i in range(1,coin_num+1):
        rate_sum_temp = rate_sum_temp + rate[i-1]
    if (state_sum == 0):
        rate_sum = 0
    else:
        rate_sum = rate_sum_temp/state_sum
    
    # Print
    minute_pre = now.minute
    hour_pre = now.hour
    day_pre = now.day

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
    
    cash_temp = 0
    for i in range(1,coin_num+1):
        cash_temp = cash_temp + btc[i-1]*current_price[i-1]

    state_sum = 0
    for i in range(1,coin_num+1):
        state_sum = state_sum + state[i-1]

    rate_accu = rate_accu + rate_sum

    if (cash < cash_virtual - 10000):
        stop_flag = 1

    print('Now Time:', now.month, '.', now.day, '.', now.hour, '/ cash:', cash + cash_temp, '/ state:', state_sum, '/ coin num:', coin_num, '/ rate sum:', rate_sum, '/ rate accu:', rate_accu)
    print('-----------------------------------------')
