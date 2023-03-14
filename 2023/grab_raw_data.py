import requests
from requests import Session

import os
import sys

import re
import time


from sys import version_info
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

CIPHERS = (
    ':@SECLEVEL=2:ECDH+AESGCM:ECDH+CHACHA20:ECDH+AES:DHE+AES:!aNULL:!eNULL:!aDSS:!SHA1:!AESCCM'
)

def environment_requires_DES_adapter():
    return version_info.major == 3 and version_info.minor < 11

class DESAdapter(HTTPAdapter):
    """
    A TransportAdapter that re-enables 3DES support in Requests to avoid Cloudflare filtering based on SSL profiling
    Adapted from the research provided by Nick Ostendorf (@nickostendorf) in https://github.com/j-andrews7/kenpompy/issues/33
    """

    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(DESAdapter, self).proxy_manager_for(*args, **kwargs)


YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023]

session = Session()
session.mount('https://kenpom.com/', DESAdapter())

browser = mechanicalsoup.StatefulBrowser(session)
browser.set_user_agent('Mozilla/5.0')
browser.open('https://kenpom.com/index.php')

browser.get_current_page()
browser.select_form('form[action="handlers/login_handler.php"]')
browser['email'] = 'lilleswing@gmail.com'
browser['password'] = os.environ['KENPOM_PASSWORD']

response = browser.submit_selected()


def get_html(url, cookie):
    headers = {
        'cookie': f"PHPSESSID={cookie}"
    }

    r = session.get(url, headers=headers)
    return r.text


def get_data_for_years(all_teams, cookie):
    for my_team in all_teams:
        for year in YEARS:
            print(f'{year}')
            team = "%s&y=%s" % (my_team, year)
            team_str = team[9:]
            team_name = team_str[5:]
            url = 'https://kenpom.com/%s' % team
            fname = 'raw_data/%s.html' % team_name
            if os.path.exists(fname):
                continue
            html = get_html(url, cookie)
            with open(fname, 'w') as fout:
                fout.write(html)
            time.sleep(0.25)

def list_teams(cookie):
    cookies = {
        'PHPSESSID': f'{cookie}',
    }

    headers = {
        'authority': 'kenpom.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="111", "Not(A:Brand";v="8", "Chromium";v="111"',
        'sec-ch-ua-mobile': '?0',
        'PHPSESSID': f'{cookie}',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36',
    }

    index_page = requests.get('https://kenpom.com/', cookies=cookies, headers=headers).content
    print(index_page)
    all_teams = re.findall('team.php.team=.*?"', str(index_page))[:-1]
    return all_teams
            
            
def main():
    cookie = sys.argv[1]
    all_teams = list_teams(cookie)
    all_teams = [x[:-1] for x in all_teams]  # remove the " at the end I matched

    if not os.path.exists('raw_data'):
        os.mkdir('raw_data')

    get_data_for_years(all_teams, cookie)


if __name__ == "__main__":
    main()
