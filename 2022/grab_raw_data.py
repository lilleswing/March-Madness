import requests
import os
import sys

import re
import time

YEARS = [2016, 2017, 2018, 2019, 2020, 2021, 2022]


def get_html(url, cookie):
    headers = {
        'cookie': f"PHPSESSID={cookie}"
    }

    r = requests.get(url, headers=headers)
    return r.text


def get_data_for_years(all_teams, cookie):
    for my_team in all_teams:
        for year in YEARS:
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


def main():
    cookie = sys.argv[1]
    index_page = requests.get('https://kenpom.com/').content
    all_teams = re.findall('team.php.team=.*?"', str(index_page))[:-1]
    all_teams = [x[:-1] for x in all_teams]  # remove the " at the end I matched

    if not os.path.exists('raw_data'):
        os.mkdir('raw_data')

    get_data_for_years(all_teams, cookie)


if __name__ == "__main__":
    main()
