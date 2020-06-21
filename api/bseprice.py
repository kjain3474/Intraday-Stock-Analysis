import requests
import json
from bs4 import BeautifulSoup
import pandas as pd


def getBseIntraday(cSymbol):

    response = requests.get("https://api.bseindia.com/Msource/90D/getQouteSearch.aspx?Type=EQ&text={}&flag=gq".format(cSymbol.upper()))

    soup = BeautifulSoup(response.content, features="html.parser")

    scripcode = soup.find("li", class_="quotemenu").a['href'].split('/')[-2]

    response = requests.get("https://api.bseindia.com/BseIndiaAPI/api/StockReachGraph/w?scripcode={}&flag=0&fromdate=&todate=&seriesid=".format(scripcode))

    data = response.json()
    
    stockdata = json.loads(data['Data'])

    df = pd.json_normalize(stockdata).drop(columns=['vole'])

    df = df.rename({'dttm': 'bsetime', 'vale1': 'bseval'}, axis=1)

    df['bseval'] = pd.to_numeric(df['bseval'])

    df['bsetime'] = df['bsetime'].apply(lambda x: x.split(" ")[-1])

    df['bsetime'] = pd.to_datetime(df['bsetime'], format='%H:%M:%S').dt.strftime('%H:%M')

    df = df.drop(df[df['bsetime'] > "15:30"].index)

    cols = ['bsetime', 'bseval']
    lst = []
    currMin = 0
    currHour = 0
    currRow = None
    total = len(df.index)
    for index, row in df.iterrows():
        if index == 0:
            currhour = int(row.bsetime.split(":")[0])
            currMin = int(row.bsetime.split(":")[1])
            currRow = row
        elif index < total - 1:
            hour = int(row.bsetime.split(":")[0])
            minute = int(row.bsetime.split(":")[1])

            if hour >= currhour and minute > currMin:
                lst.append(currRow)

            currHour = hour
            currMin = minute
            currRow = row
        elif index == total - 1:
            lst.append(row)

    df = pd.DataFrame(lst, columns=cols)

    return df