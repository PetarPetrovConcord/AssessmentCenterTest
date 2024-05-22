import requests
import json
import atexit
from datetime import datetime, timezone
import sys
import urllib.parse

amount = None
baseCurrency = None
toCurrency = None
cacheExchangeRatesDictionary = {}
allCurrencies = {}
allConversionsDictionary = { "conversions": [] }
date = None

def getFromApi():
  query_params["from"] = baseCurrency
  query_params["date"] = date
  exchangeRatesResponse = requests.get(historicalExchangeRatesUrl, headers = headers, params=query_params)
  if exchangeRatesResponse.status_code == 200:
    ratesJson = exchangeRatesResponse.json()
    amountToBeSavedAndPrinted = "{:.2f}".format(amount * ratesJson['results'][toCurrency])
    cacheExchangeRatesDictionary[baseCurrency] = {
      "exchangeRateDate": ratesJson['date'],
      "results": ratesJson['results']
    }
    allConversionsDictionary["conversions"].append({
      "exchangeRateDate": ratesJson['date'],
      "amount": amount,
      "baseCurrency": baseCurrency,
      "currencyToConvertTo": toCurrency,
      "resultingAmount": float(amountToBeSavedAndPrinted)
    })
    print(str(amount) + " " + baseCurrency + " is " + amountToBeSavedAndPrinted + " " + toCurrency)

def exit_handler():
    with open(f"Conversions_{date}.json", 'w', encoding='utf-8') as f:
          json.dump(allConversionsDictionary, f, ensure_ascii=False, indent=4)


atexit.register(exit_handler)
headers = {"accept": "application/json"}
baseUrl = "https://api.fastforex.io"
currenciesUrl = f"{baseUrl}/currencies"
historicalExchangeRatesUrl = f"{baseUrl}/historical"
query_params = { }

with open('config.json', 'r') as json_file:
  data = json.load(json_file)
  api_key = data.get('api_key')
  query_params["api_key"] = api_key
  if len(sys.argv) == 2:
    date = sys.argv[1]

  allCurrenciesResponse = requests.get(currenciesUrl, headers = headers, params=query_params)
  if allCurrenciesResponse.status_code == 200:
    allCurrencies = allCurrenciesResponse.json()['currencies']

  while True:
    while True:
      temp = input()
      try:
          
          amount = int(temp)
          break
      except ValueError:
        try:
            if len(temp[temp.rfind('.')+1:]) != 2:
              raise ValueError('Must have two numbers after decimal point')
            amount = float(temp)
            break
        except ValueError:
          temp = temp.upper()
          if temp == "END":
            exit()
          print("Please enter a valid amount")

    while True:
      temp = input()
      temp = temp.upper()
      if temp == "END":
        exit()
      if temp in allCurrencies:
        baseCurrency = temp
        break
      else:
        print("Please enter a valid currency code")

    while True:
      temp = input()
      temp = temp.upper()
      if temp == "END":
        exit()
      if temp in allCurrencies:
        toCurrency = temp
        break
      else:
        print("Please enter a valid currency code")

    if baseCurrency in cacheExchangeRatesDictionary:
      d1 = datetime.strptime(cacheExchangeRatesDictionary[baseCurrency]["exchangeRateDate"], "%Y-%m-%d")
      if abs((datetime.now().astimezone(tz=timezone.utc) - d1.replace(tzinfo=timezone.utc)).seconds) > 300:
        getFromApi()
      else:
        amountToBeSavedAndPrinted = "{:.2f}".format(amount * cacheExchangeRatesDictionary[baseCurrency]['results'][toCurrency])
        allConversionsDictionary["conversions"].append({
            "exchangeRateDate": cacheExchangeRatesDictionary[baseCurrency]['exchangeRateDate'],
            "amount": amount,
            "baseCurrency": baseCurrency,
            "currencyToConvertTo": toCurrency,
            "resultingAmount": float(amountToBeSavedAndPrinted)
          })
        print(str(amount) + " " + baseCurrency + " is " + amountToBeSavedAndPrinted + " " + toCurrency)
    else:
      getFromApi()