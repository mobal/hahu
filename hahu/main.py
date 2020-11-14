from bs4 import BeautifulSoup
import argparse
import requests

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
filter_list = 'PDNG2VG3R3NDAEH5S56ACCKQW3PMOVVLEJK2QUVFXZDAGGMC6FSZB3KEBMV75PPDHAV6ELCPDGOWHT44TE4Q5CHFIZ6HQUKWUJIBBMBFE5QYO7PRZJMCSCT7IOB7UCS5UAAVVCICOR7HBR7YRMUPNVGLQAQSIIG65UY2ABSXDNU6HXMFFCFDSA7PKNTC2CXMLSO53WZ5EPRLLXJI44CP4ZSBQ75AZTTUIMPFDFGDO4RYUFQ43CBQILP5SMBVK3AQGTMSOHGX3SRUG7OCIBH6QWCZXKDBL6I6DLLFBPHOYURGH2ANZYA44MDK4UXI6LE7Z5XBW6SMNHCCNXKOYHHU5OIVQ67NHQOH5KWLWWQMGJPOMMT6PB3XYTENQ7ZYWDH6IXL4WA72IRKFZYGQ7FAONN7U4GHSGQ2BSLOTNCP6GZOPXN65RX6Q5BNYRYA2PIEWZUUGAM6M4E56HVFA2YR3CZDCXUMW6BDZ5H6BT5LM7PMPGOBBPT5GEFM3FFLV7WGMDPOL7EWRMCOAYWGVQ4OINTPFZI4IS62242IW2GUCGJZ4WZKUS2L7K53MOGYFO2FTZRU5D55BGJUA2FYKSFP6PPAUMWFKWGCXFFPMM6EZ4JKYYVZJLYTZ3LHZQS3ELV5ZGALZU47Z5PQAZ3BHKI2VXVWAVS6U5I6HV4KLPR7T25UG5JEG62VPRWDZGXYUCGYIGDOTCHZG55XYUXNPUY4BWQT2HLFPOKKYGKFBUVMI63YTL3BVVCMWCQDX5RRSXJZQPNJGS2LAOY2KBOKEHVMYLYLVI3T54FGZNM76K6CO5AXTH4J5LE5JDIZWZPBPXYY4NCX6R2ZDXELLJSIUNXJO7CD7CMH7JHWGZXH6AJY5HKBXMIXM7YP5YHU2T4'

args = parser.parse_args()

def __get(url):
    res = requests.get(url, headers={'User-Agent': args.user_agent})
    if res.ok:
        return res.content

def __parse(html):
    return BeautifulSoup(html, 'html.parser')

def crawl(url):
    html = __get(url)
    soup = __parse(html)
    print(soup.title)

def main():
    crawl(base_url + '/' + filter_list + '/page1')

if __name__ == '__main__':
    main()
