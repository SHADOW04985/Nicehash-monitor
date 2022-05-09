from nicehashlib import private_api
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
from configparser import ConfigParser

class pullbot:
  def apikeys():
    
    cf_obj = ConfigParser()
    Host = 'https://api2.nicehash.com'
    cf_obj.read('config.ini')
    orgid=cf_obj.get('details','org_id')
    key=cf_obj.get('details','key')
    secret=cf_obj.get('details','secret')
    rigid=cf_obj.get('details','rigid')
    
    api_pull=private_api(Host,orgid,key,secret,rigid)
      
    return api_pull
  
  def btcprice():
    cf_obj = ConfigParser()
    cf_obj.read('config.ini')
    currency=cf_obj.get('details','currency')
    if currency == 'DLR':
      url = "https://www.google.com/search?q=bitcoin+price+in+usd"
    elif currency == 'RUPE':
      url = "https://www.google.com/search?q=bitcoin+price+in+inr"
    elif currency == 'EUR':
      url = "https://www.google.com/search?q=bitcoin+price+in+eur"
    response = requests.get(url)
    soup = bs(response.text,'html.parser')
    price = soup.find('div',attrs={'class':'BNeawe iBp4i AP7Wnd'}).text
    btcprice = list(price.split(" "))
    btcprice = float(btcprice[0].replace(",",""))
    return btcprice

  def local_time():
    now = datetime.now()
    curr_time = now.strftime("%H:%M:%S")
    return curr_time

  def getTemps(sublst):
    temp=[]
    try:
      for i in range(6):
        tmps=sublst[i]['temperature']
        temp.append(tmps)
    except IndexError:
      return temp
