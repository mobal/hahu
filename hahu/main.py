from bs4 import BeautifulSoup
import argparse
import json
import logging
import math
import requests
import sys

log = logging.getLogger(__name__)
parser = argparse.ArgumentParser(description='Hasznaltauto crawler',
                                prog='hahu')
parser.add_argument('--config',
                    default='config.json',
                    help='path to the configuration file',
                    nargs='?')
parser.add_argument('--user-agent',
                    default='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:82.0) Gecko/20100101 Firefox/82.0',
                    help='User-Agent',
                    nargs='?')
base_url = 'https://www.hasznaltauto.hu'

args = parser.parse_args()
logging.basicConfig(stream=sys.stdout, level=logging.INFO)
page_size = 20

def __get(url):
    res = requests.get(url, headers={'User-Agent': args.user_agent})
    if res.ok:
      return res.content
    else:
      log.error(res.status_code)
      sys.exit(res.status_code)


def __parse(divs):
  if (len(divs) > 0):
    for div in divs:
      a = div.find('h3').find('a', href=True)
      details = div.find('div', {'class': 'talalatisor-info adatok'})
      price = div.find('div', {'class': 'vetelar'})
      log.info(a.text)
      log.info(a['href'])
      log.info(details.text)
      log.info(price.text)

def __post(url, headers, payload):
  res = requests.post(url, data=payload, headers=headers)
  if res.ok:
    return res
  else:
    log.error(res.status_code)
    sys.exit(res.status_code)

def __get_search_url():
  headers = {
    'Accept': 'application/json, text/javascript, */*, q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': args.user_agent,
    'Content-Type': 'Application/X-WWW-Form-URLEncoded; Charset=UTF-8'
  }
  payload = {
    'HirdetesSzemelyautoSearch[marka_id]': 146,
    'HirdetesSzemelyautoSearch[modell_id]': 1679,
    'HirdetesSzemelyautoSearch[evjarat_min]': 2015,
    'HirdetesSzemelyautoSearch[kivitel][]': 120,
    'HirdetesSzemelyautoSearch[vetelar_min]': 2750000,
    'HirdetesSzemelyautoSearch[vetelar_max]': 3500000,
    'HirdetesSzemelyautoSearch[uzemanyag][]': 1,
    'getSearchUrl': 1
  }
  return json.loads(__post(base_url + '/egyszeru/szemelyauto', headers, payload).content)['formUrl'].rsplit('/', 1)[-1]

def __get_total():
  headers = {
    'Accept': 'application/json, text/javascript, */*, q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': args.user_agent,
    'Content-Type': 'Application/X-WWW-Form-URLEncoded; Charset=UTF-8'
  }
  payload = {
    'HirdetesSzemelyautoSearch[marka_id]': 146, # Volkswagen
    'HirdetesSzemelyautoSearch[modell_id]': 1679, # Golf
    'HirdetesSzemelyautoSearch[evjarat_min]': 2015, # Year min
    'HirdetesSzemelyautoSearch[kivitel][]': 120, # Hatchback
    'HirdetesSzemelyautoSearch[vetelar_min]': 2750000, # Min. price in HUF ~ € 7605
    'HirdetesSzemelyautoSearch[vetelar_max]': 3500000, # Max. price in HUF ~ € 9678
    'HirdetesSzemelyautoSearch[uzemanyag][]': 1 # Fuel, petrol
  }
  return json.loads(__post(base_url + '/egyszeru/szemelyauto', headers, payload).content)['totalCount']
  

def crawl():
  curr = 0
  last = math.ceil(__get_total() / page_size)
  search_key = __get_search_url()
  while curr < last:
    url = base_url + '/talalatilista' + '/' + search_key + '/page' + str(curr + 1)
    log.info(url)
    res = __get(url)
    __parse(BeautifulSoup(res, 'html.parser').find_all('div', {'class': 'talalati-sor'}))
    if curr == 0:
      l = BeautifulSoup(res, 'html.parser').find('li', {'class': 'last'})
      last = 1 if l == None else int(l.text)
    curr += 1

def main():
    crawl()

if __name__ == '__main__':
    main()
