from bs4 import BeautifulSoup
from dotenv import load_dotenv
import base64
import json
import logging
import math
import os
import requests
import sys

BASE_URL = 'https://www.hasznaltauto.hu'
PAGE_SIZE = 20

load_dotenv()

log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

payload = {
  'HirdetesSzemelyautoSearch[marka_id]': os.getenv('CAR_MAKE'),
  'HirdetesSzemelyautoSearch[modell_id]': os.getenv('CAR_MODEL'),
  'HirdetesSzemelyautoSearch[evjarat_min]': os.getenv('CAR_MIN_YEAR'),
  'HirdetesSzemelyautoSearch[kivitel][]': os.getenv('CAR_BODY_TYPE'),
  'HirdetesSzemelyautoSearch[vetelar_max]': os.getenv('CAR_MAX_PRICE'),
  'HirdetesSzemelyautoSearch[vetelar_min]': os.getenv('CAR_MIN_PRICE'),
  'HirdetesSzemelyautoSearch[uzemanyag][]': os.getenv('CAR_FUEL_TYPE')
}

def __crawl(url):
  return __parse(BeautifulSoup(__get(url).content, 'html.parser').find_all('div', {'class': 'talalati-sor'}))

def __get(url, stream=False):
  res = requests.get(url, headers={'User-Agent': os.getenv('USER_AGENT')},stream=stream)
  if res.ok:
    return res
  else:
    log.error(res.status_code)
    sys.exit(res.status_code)

def __get_image_as_base64_string(url):
  return str(base64.b64encode(__get(url, True).content).decode('utf-8'))

def __get_search_key():
  headers = {
    'Accept': 'application/json, text/javascript, */*, q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': os.getenv('USER_AGENT'),
    'Content-Type': 'Application/X-WWW-Form-URLEncoded; Charset=UTF-8'
  }
  return json.loads(__post(BASE_URL + '/egyszeru/szemelyauto', dict(payload, getSearchUrl=1), headers).content)['formUrl'].rsplit('/', 1)[-1]

def __get_total():
  headers = {
    'Accept': 'application/json, text/javascript, */*, q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': os.getenv('USER_AGENT'),
    'Content-Type': 'Application/X-WWW-Form-URLEncoded; Charset=UTF-8'
  }
  return json.loads(__post(BASE_URL + '/egyszeru/szemelyauto', payload, headers).content)['totalCount']

def __parse(divs):
  if (len(divs) > 0):
    cars = []
    for div in divs:
      a = div.find('h3').find('a', href=True)
      details = div.find('div', {'class': 'talalatisor-info adatok'})
      img = div.find('img', {'class': 'img-responsive'})
      price = div.find('div', {'class': 'vetelar'})
      cars.append({
        'details': details.text,
        'image': __get_image_as_base64_string(img['data-lazyurl'].replace('_1t', '')),
        'price': price.text,
        'title': a.text,
        'url': a['href']
      })
    return cars
  return []

def __post(url, payload, headers={'User-Agent': os.getenv('USER_AGENT')}):
  res = requests.post(url, data=payload, headers=headers)
  if res.ok:
    return res
  else:
    log.error(res.status_code)
    sys.exit(res.status_code)

def main():
  cars = []
  curr = 0
  last = math.ceil(__get_total() / PAGE_SIZE)
  search_key = __get_search_key()
  while curr < last:
    cars.append(__crawl(BASE_URL + '/talalatilista' + '/' + search_key + '/page' + str(curr + 1)))
    curr += 1
  log.info(cars)

if __name__ == '__main__':
  main()
