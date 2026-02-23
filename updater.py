import os
import requests
import json
import yfinance as yf
from datetime import datetime

def get_fred_val(series_id):
    api_key = os.getenv('FRED_API_KEY')
    if not api_key:
        print(f"BŁĄD: Brak klucza API dla {series_id}. Sprawdź GitHub Secrets!")
        return 0.0
    
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json&sort_order=desc&limit=1"
    try:
        response = requests.get(url)
        data = response.json()
        if 'observations' in data and len(data['observations']) > 0:
            val = data['observations'][0]['value']
            return float(val) if val != '.' else 0.0
        else:
            print(f"Błąd API FRED ({series_id}): {data.get('error_message', 'Brak danych w odpowiedzi')}")
            return 0.0
    except Exception as e:
        print(f"Błąd połączenia dla {series_id}: {e}")
        return 0.0

try:
    print("Pobieram dane płynności...")
    # Pobieranie głównych składników płynności
    walcl = get_fred_val('WALCL')    # Bilans
    tga = get_fred_val('WTREGEN')    # TGA
    rrp = get_fred_val('RRPONTS')    # ON RRP
    
    # Obliczanie Net Liquidity (w miliardach)
    net_liq = round((walcl / 1000) - (tga / 1000) - rrp, 1) if walcl > 0 else 0.0
    
    print("Pobieram dane rynkowe...")
    spx_data = yf.Ticker("^GSPC").fast_info
    spx_val = round(spx_data['last_price'], 0)

    output = {
        "last_update": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "net_liq": net_liq,
        "spx": spx_val,
        "tga": round(tga / 1000, 1),
        "rrp": round(rrp, 1),
        "sofr": get_fred_val('SOFR'),
        "iorb": get_fred_val('IORB')
    }

    with open('data.json', 'w') as f:
        json.dump(output, f, indent=2)
    print("Plik data.json został pomyślnie zaktualizowany!")

except Exception as e:
    print(f"Krytyczny błąd skryptu: {e}")
    exit(1)
