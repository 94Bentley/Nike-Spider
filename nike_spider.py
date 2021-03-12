import requests
from fake_useragent import UserAgent
import logging
import json
import sys
import os
from urllib import parse

BASE_URL = 'https://api.nike.com/cic/browse/v1'
UA = UserAgent()
KEYWORD = ''
LIMIT = 24
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def scrape_api(url, params):
    full_url = url + '?' + parse.urlencode(params)
    logging.info('scraping %s', full_url)
    headers = {'User-Agent': UA.random}
    try:
        response = requests.get(url=full_url, headers=headers)
        if response.status_code == 200:
            return response.json()
        logging.error('get invalid status code %s while scraping %s', response.status_code, full_url)
    except Exception:
        logging.error('error occurred while scraping %s', full_url, exc_info=True)


def get_total():
    try:
        total_page = scrape_data(0)['data']['products']['pages'].get('totalPages')
    except Exception:
        logging.error('no result found', exc_info=True)
        sys.exit()
    logging.info(f'keyword:{KEYWORD} total page:{total_page}')
    return total_page


def scrape_data(offset):
    params = {
        'queryid': 'products',
        'anonymousId': 'BCA14B1A2A9556B839BA4957D5FB9D94',
        'endpoint': '/product_feed/rollup_threads/v2?filter=marketplace(CN)&filter=language(zh-Hans)&filter=employeePrice(true)&searchTerms={keyword}&anchor={offset}&consumerChannelId=d9a5bc42-4b9c-4976-858a-f159cf99c647&count={limit}'.format(
            keyword=KEYWORD, offset=offset, limit=LIMIT),
    }
    return scrape_api(BASE_URL, params)


def save_data(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    global KEYWORD
    KEYWORD = input('请输入关键词：')
    total_page = get_total()
    os.path.exists(f'{KEYWORD}') or os.makedirs(f'{KEYWORD}')
    for page in range(1, total_page + 1):
        data = scrape_data((page - 1) * 24)
        if not data:
            continue
        logging.info('saving data page %s', page)
        save_data(data, f'{KEYWORD}/{KEYWORD}{page}.json')


if __name__ == '__main__':
    main()
