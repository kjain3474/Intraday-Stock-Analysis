from django.urls import path

from . import views

urlpatterns = [
    path('intraday/chart/company', views.chart, name='intradayChart'),
    path('intraday/data/company', views.data, name='intradayData'),
]