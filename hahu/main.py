from bs4 import BeautifulSoup
import argparse
import logging
import requests
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

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
base_url = 'https://www.hasznaltauto.hu/talalatilista'
filter_list = 'PDNG2VG3N3NTADH5C57UD3BEZWTD43RICZQAQBQM3CV4DREMUPUMEQESRUTEL7T5STWLNFU3E4J6OSHEEF4WIEGLE7Y6MRKZRFBEDQEWTSCB35WFGNR2KKH4BUG6UK3UQEJLIEQF5D6OA3WEJ7JDKGGQ67IIBPYVZ553CGET6QGGW4FVSE3CMWMIUKMDH4B2MXLKFQGO2XM33XJDEJPPXKGPKUW6QUE7YGMS5ZIRIWM34G2RWTQMAHRENDUR6HFIMKT2BSJ64C4OMHQ55IJQM6SAP52E4L3QBZYIMUIR65ZGJEJ4RNWUGI2WPZQJHHVG4B5T6LGYUHXXJ4FRA2V2WFVJ3C37TGD7PB37ZHANR7QBOGP4ROXJOB7UANIXDAKD44BZTX6SQ47Y4DAFJF3NWDHUKO5PM353DO5UVBNYRYA2PIEWZUUGBE527XHDQNNI6VECZGKYN7DBWQK6HJ7UMPO3GH3DYNAI57NV7RLGZLKRONTTAD326ZBPINGANLHKJUTDG4NZGJHOEPVM5TEK4DCBTG43CMRKZPF7UO3WGTMCXNCZ4ZQZ352UDG2IMC4FZCXXGXUKOKEKWGCXIO6IZ4LSRBLTCXQN6F5NBSM2J5UFW5E5BNZ2COMXX4A45QD6EJK3GMINZTNOWND27RFHC6Z4P6G6MRRKWVL4LN6NVOE67V2AQDUY56JQPF7VH3DNGXC5SEGS2NI34TWBSJI5JKCCWSH26YNPIHGQYA52MMPVWOMF3GJUUSYDWORQDTJF5LESVJBXDCOXWU3EV76ZJYZZUG74ZRHXMTUUJDW2FQF67D3TUC62FL4P4RNNAJSTWQMX4OX4GP4EJ36DXD4RT7FEINT5ATUE3X7QGQEGSUDA'

args = parser.parse_args()

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

def crawl():
  curr = 0
  last = 1
  while curr < last:
    url = base_url + '/' + filter_list + '/page' + str(curr + 1)
    res = __get(url)
    __parse(BeautifulSoup(res, 'html.parser').find_all('div', {'class': 'talalati-sor'}))
    if curr == 0:
      l = BeautifulSoup(res, 'html.parser').find('li', {'class': 'last'})
      last = 1 if l == None else int(l.text)
      log.info(last)
    curr += 1

def main():
    crawl()

if __name__ == '__main__':
    main()
