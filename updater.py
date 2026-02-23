import os
import requests
import json
import yfinance as yf
from datetime import datetime

def get_fred_val(series_id):
    api_key = os.getenv('FRED_API_KEY')
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
    return float(requests.get(url).json()['observations'][0]['value'])

# Pobieranie danych live
data = {
    "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
    "net_liq": round((get_fred_val('WALCL')/1000) - (get_fred_val('WTREGEN')/1000) - get_fred_val('RRPONTS'), 1),
    "spx": round(yf.Ticker("^GSPC").fast_info['last_price'], 0),
    "sofr": get_fred_val('SOFR'),
    "iorb": get_fred_val('IORB'),
    "tga": round(get_fred_val('WTREGEN')/1000, 1)
}

with open('data.json', 'w') as f:
    json.dump(data, f)
