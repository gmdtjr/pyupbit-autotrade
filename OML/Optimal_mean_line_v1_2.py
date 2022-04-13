from dataclasses import asdict
from os import lseek
import time
import pyupbit
import datetime
import schedule
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

def get_past_price(ticker, load_day):
    #"""Current Price Check"""
    past_price = np.zeros(200)

    for i in range(10):
        df_m = pyupbit.get_ohlcv(ticker, interval="minute1", to=load_day) ## 1분 단위
        if (not df_m is None):
            break

    if (not df_m is None):
        for i in range(0,200):
            past_price[i] = df_m['open'][i]
    
    return past_price

# Log-In
print("autotrade start")

# Initial flag setting
coin_list = ['KRW-ETH', 'KRW-NEO', 'KRW-MTL', 'KRW-LTC', 'KRW-XRP',
            'KRW-ETC', 'KRW-OMG', 'KRW-SNT', 'KRW-WAVES', 'KRW-XEM',
            'KRW-QTUM', 'KRW-LSK', 'KRW-STEEM', 'KRW-XLM', 'KRW-ARDR',
            'KRW-ARK', 'KRW-STORJ', 'KRW-GRS', 'KRW-REP']
coin_num = len(coin_list)
p_list = [16, 84, 86, 95, 110, 
        76, 10, 77, 79, 88, 
        79, 96, 64, 16, 82,
        21, 77, 21, 107]
q_list = [23, 92, 141, 97, 116, 
        135, 106, 80, 125, 105,
        86, 100, 66, 22, 87,
        133, 86, 139, 108]


## Load Day Initialize
class Time: 
    year: int = 0
    month: int = 0
    day: int = 0
    hour: int = 0
    minute: int = 0
    second: int = 0

now = Time()

##now_current = datetime.datetime.now()

## 과거 데이터 쌓기
data = np.zeros((coin_num, 60*144))
past_price = np.zeros(200)
for i in range(0,coin_num):
    now_current = now
    now_current.year = 2022
    now_current.month = 2
    now_current.day = 28
    now_current.hour = 23
    now_current.minute = 59
    ##now_current = datetime.datetime.now()
    now.year = now_current.year
    now.month = now_current.month
    now.day = now_current.day
    now.hour = now_current.hour
    now.minute = now_current.minute
    kkk = 0
    for j in range(0,60*144):
        minute_interval = -1
        ## Time Update
        now.minute = now.minute + minute_interval
        if (now.minute < 0):
            now.minute = 59
            now.hour = now.hour - 1
        if (now.hour < 0):
            now.hour = 23
            now.day = now.day - 1
            if (now.month == 5 or now.month == 7 or now.month == 10 or now.month == 12):
                if (now.day < 0):
                    now.day = 30
                    now.month = now.month - 1

            if (now.month == 2 or now.month == 4 or now.month == 6 or now.month == 9 or now.month == 11 or now.month == 1 or now.month == 8):
                if (now.day < 0):
                    now.day = 31
                    now.month = now.month - 1
                    if (now.month < 0):  ## 윤달은 나중에 고려 어차피 2023년
                        now.month = 12
                        now.year = now.year - 1
            if (now.month == 3):
                if (now.day < 0):
                    now.day = 28
                    now.month = now.month - 1

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

        if (kkk == 0):
            sleep(0.1)
            past_price = get_past_price(coin_list[i], load_day)
            #print(past_price)
        elif (kkk >= 199):
            kkk = -1

        data[i,j] = past_price[kkk]

        kkk = kkk + 1
     
# 데이터 0있으면 이전 값으로 채우기
for i in range(0,coin_num):
    for j in range(0,60*144):
        if data[i,j] == 0:
            data[i,j] = data[i,j-1]

## 평균 구하기
p_mean = np.zeros(coin_num)
q_mean = np.zeros(coin_num)

for i in range(0,coin_num):
    sum_temp = 0
    sum_ind = 0
    for j in range(0,60*p_list[i]):
        sum_temp = sum_temp + data[i,j]
        sum_ind = sum_ind + 1
    p_mean[i] = sum_temp/sum_ind

    sum_temp = 0
    sum_ind = 0
    for j in range(0,60*q_list[i]):
        sum_temp = sum_temp + data[i,j]
        sum_ind = sum_ind + 1
    q_mean[i] = sum_temp/sum_ind

print("Initializing: ", now.hour,'/',now.minute,'/',now.second)

## Initialize flag
update_flag = 0
state = np.zeros(coin_num)

cash = 20000000
btc = np.zeros(coin_num)

now_current = now
now_current.year = 2022
now_current.month = 1
now_current.day = 31
now_current.hour = 23
now_current.minute = 59

# Autotrading Start
while (not (now.year == 2022 and now.month == 3)):

    #now_current = datetime.datetime.now()
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

    if update_flag == 0:
        
        for i in range(0,coin_num): 
        # data 밀고 현재 값 넣기
            for j in range(0,60*144-1):
                j_temp = (60*144-1) - j
                data[i,j_temp] = data[i,j_temp-1]
            sleep(0.1)
            current_price = get_current_price(coin_list[i], load_day)
            data[i,0] = current_price
        
        ## 평균 구하기
        p_mean = np.zeros(coin_num)
        q_mean = np.zeros(coin_num)

        for i in range(0,coin_num):
            sum_temp = 0
            sum_ind = 0
            for j in range(0,60*p_list[i]):
                sum_temp = sum_temp + data[i,j]
                sum_ind = sum_ind + 1
            p_mean[i] = sum_temp/sum_ind

            sum_temp = 0
            sum_ind = 0
            for j in range(0,60*q_list[i]):
                sum_temp = sum_temp + data[i,j]
                sum_ind = sum_ind + 1
            q_mean[i] = sum_temp/sum_ind

        update_flag = 1
        update_minute = now_current.minute
    elif (now_current.minute != update_minute):
        update_flag = 0
    # 전략
    for i in range(0,coin_num):
        ticker = coin_list[i]
        if (state[i] == 0):
            if (p_mean[i] > q_mean[i]):
                sleep(0.1)
                cp = data[i,0]
                buy_val = 1000000
                if krw > buy_val:
                    krw = buy_val
                    btc[i] = btc[i] + (0.9995*krw/cp) 
                    cash = cash - krw
                elif krw <= buy_val and krw > 10000:
                    krw = cash
                    btc[i] = btc[i] + (0.9995*krw/cp) 
                    cash = cash - krw
                state[i] = 1
        if (state[i] == 1):
            if (p_mean[i] < q_mean[i]):
                sleep(0.1)
                cp = data[i,0]
                cash = cash + (0.9995*btc[i]*cp) 
                btc[i] = 0
                state[i] = 0
    # State Sum
    state_sum = 0
    for i in range(0,coin_num):
        state_sum = state_sum + state[i]
    cash_temp = 0
    for i in range(0,coin_num):
        cash_temp = cash_temp + btc[i]*data[i,0]
    # Print
    print('Now Time:', now.month, '.', now.day, '.', now.hour, '.', now.minute, ',', now.second,'/ cash:', cash + cash_temp)
    print('state sum:', state_sum)
    print('state:', state[0], '/ cp:', cp[0], '/ buy val:', buy_val[0])
    print('---------------------------------')
    time.sleep(1)
