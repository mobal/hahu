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
filter_list = 'PDNG2VGRR2RTADH4C47GAVJIFRW7N4KWU6VXJKSOHLUV5EK3LSNCMIKVCLILNK767M4QTXIFLJPLBRTGHSPDQAC3X2ZE7S6SRQSQEHBW3JYNQYU7XQIZNMWELZI2DPCA452IA4UWQCOBM3QH7TEE3DIONUHTLWDL6K3GHC4BUQTVRAVJCRXT2SOJSKWCYFXUETZQF6AYBKLNS52BYEJOYTBVMGUVSWJOK4X2WUAVT76FTLJHVTMTVTMLS72WF7P53Q2ZHUQWUSVU4YCUC65LCJANN4JNDAEBO3HUC4X3UQQPH3UA2TWZGHGJ3CQUC6KEU6P2JP642I76DZHAASBYWC4WDREDP6NXVH2YBJK7LCOPYAPUENXKG2YGNUTZ35J5JBORN3K3ZWH6NBZVQ6A2OCAW7TJAV75C5H4R5Q5XEQRVAUEXPVTZ2VV7XF2X7DCW3JY523XKKHGWWIHYW7MQ544FS3KFDAIRKDYXVECSQ245PBHLDKSRYESLJIKOL4EF4PT45HSQR3EP3GGYSN66B3V3SP53DUX4EENROZ7YR2OBBPHHZ2JQDKP24RQRLKK55I63TRODHPIE4OZH2SO7VXTUSKNPBEX6R3XAHNAXNATMZ4LAN6QTGSAJM7WXZPUY4Y4UWY447E4IX4OSY7FRRZZ6ZZRVYRE5UT4YQ3MDUYZW4LTUTKNSR5O62BTGSUORRIVJRDOXJG2PRGFC6HEH7CPKVJCRQL7TP4DDUGT77MKTQGE7GEKWW25PQK3FZDDRLIEG55MBP6GMDFCQSQUJZXZBLPAU5AUYFUGMRDRWXLSWHGFWKNEK4YCW5JIJ3PM6JGDXAG75BZPYK3RP7U4EOPVBHXH4J5522VDW25BTMGQ7GIYONQXWRK4DGYGUQNKRKTDH6FP5C27NCW5UTOXMDO66O4FNXENQ3N7VUVNB5M'

args = parser.parse_args()

def __get(url):
    res = requests.get(url, headers={'User-Agent': args.user_agent})
    if res.ok:
        return res.content

def __parse(soup):
  for d in soup.findAll('div', {'class': 'talalati-sor'}):
    a = d.find('h3').find('a', href=True)
    details = d.find('div', {'class': 'talalatisor-info adatok'})
    price = d.find('div', {'class': 'vetelar'})
    log.info(a.text)
    log.info(a['href'])
    log.info(details.text)
    log.info(price.text)

def crawl(url):
    __parse(BeautifulSoup(__get(url), 'html.parser'))

def main():
    crawl(base_url + '/' + filter_list + '/page1')

if __name__ == '__main__':
    main()
