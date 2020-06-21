import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def getNseIntraday(cSymbol):

    url = "https://www.nseindia.com/api/chart-databyindex?index={}EQN".format(cSymbol.upper())

    headers = {
        'host': 'www.nseindia.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'Accept' : '*/*',
        'Connection': 'keep-alive'
    }

    response = requests.request("GET", url, headers=headers)

    data = response.json()

    stockdata = data['grapthData']

    df = pd.DataFrame(stockdata, columns = ['nsetime', 'nseval'])  

    df['nsetime'] = pd.to_datetime(df['nsetime'], unit='ms').dt.strftime('%H:%M')

    df = df.drop(df[df['nsetime'] > "15:30"].index) 

    cols = ['nsetime', 'nseval']
    lst = []
    currMin = 0
    currHour = 0
    currRow = None
    total = len(df.index)
    for index, row in df.iterrows():
        if index == 0:
            currhour = int(row.nsetime.split(":")[0])
            currMin = int(row.nsetime.split(":")[1])
            currRow = row
        elif index < total - 1:
            hour = int(row.nsetime.split(":")[0])
            minute = int(row.nsetime.split(":")[1])

            if hour >= currhour and minute > currMin:
                lst.append(currRow)

            currHour = hour
            currMin = minute
            currRow = row
        elif index == total - 1:
            lst.append(row)

    df = pd.DataFrame(lst, columns=cols)

    return df