from django.http import HttpResponse
from django.shortcuts import render
from .bseprice import getBseIntraday
from .nseprice import getNseIntraday
from .fusioncharts import FusionCharts
from .fusioncharts import FusionTable
from .fusioncharts import TimeSeries
import requests
import json
import pandas as pd

def getStockData(cSymbol, orient):
  nseData = getNseIntraday(cSymbol)
  bseData = getBseIntraday(cSymbol)

  df1  = bseData.set_index('bsetime')
  df2  = nseData.set_index('nsetime')
  df3  = df1.join(df2,how='outer')
  try:
    df3['time'] = df2.index
  except:
    pass
  df3['difference'] = df3.apply(lambda row: float(row.bseval) - float(row.nseval), axis = 1) 

  json_data = df3.to_json(orient=orient)

  return json_data

def data(request):
    cSymbol = request.GET['symbol']
    json_data = getStockData(cSymbol, 'records')
    return HttpResponse(json_data, content_type="application/json")


def chart(request):
    cSymbol = request.GET['symbol']
    json_data = getStockData(cSymbol, 'values')
    json_schema = open('api/static/api/schema.json').read()  

    data = json_data
    schema = json_schema

    fusionTable = FusionTable(schema, data)
    timeSeries = TimeSeries(fusionTable)

    timeSeries.AddAttribute('chart', '{}')
    timeSeries.AddAttribute('caption', '{"text":"BSE VS NSE Intraday Stock Data for Stock %s"}' %cSymbol.upper())
    timeSeries.AddAttribute('extensions', '{"customRangeSelector": {"enabled": "0"}}')
    timeSeries.AddAttribute('tooltip', '{"enabled": "true", "outputTimeFormat": {Minute: " %-I:%-M %p"}, "style":{"text":""}}')
    timeSeries.AddAttribute('navigator', '{"enabled": 0}')
    
    fcChart = FusionCharts("timeseries", "stockdata", 700, 700, "chart-1", "json", timeSeries)

    return  render(request, 'index.html', {'output' : fcChart.render()})