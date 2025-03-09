import requests

import os

import re
import time


cookies = {
    'PHPSESSID': os.environ.get('PHPSESSID', ''),
    'kenpomuser': os.environ.get('KENPOMUSER', ''),
    'kenpomid': os.environ.get('KENPOMID', ''),
    '__stripe_mid': os.environ.get('STRIPE_MID', ''),
    '__stripe_sid': os.environ.get('STRIPE_SID', ''),
    'kenpomtry': os.environ.get('KENPOMTRY', ''),
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:135.0) Gecko/20100101 Firefox/135.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://kenpom.com/index.php',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Priority': 'u=0, i',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'
}

# YEARS = [2025]

YEARS = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

from urllib.parse import urlparse, parse_qs, unquote


def extract_team_and_year(url_string):
    """
    Extracts and urldecode the team name and year from a URL string.

    Args:
        url_string: The URL string to parse.

    Returns:
        A dictionary containing the team name and year, or None if
        either value cannot be extracted.  Returns empty strings for
        team and year if the parameters are present but empty.
        Handles cases where team or y parameters are missing.
    """
    try:
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)

        # Get team and year, handling missing parameters and multiple values
        team_list = query_params.get('team')
        year_list = query_params.get('y')

        team = team_list[0] if team_list else None  # Get the first value or None
        year = year_list[0] if year_list else '2025'

        if team is not None:
            team = unquote(team)
        if year is not None:
            year = unquote(year)

        # Handle cases where parameters are present but empty
        if team == "":
            team = ""  # Or you could return None, depending on your needs
        if year == "":
            year = ""
        year = year.strip('"')
        team = team.strip('"')

        return {"team": team, "year": year}

    except Exception as e:
        print(f"Error parsing URL: {e}")
        return None  # Or raise the exception, depending on your error handling


def get_html(team, year):
    params = {
        'team': team,
        'y': year,
    }

    print(params)
    response = requests.get('https://kenpom.com/team.php', params=params, cookies=cookies, headers=headers)
    return response.text


def get_data_for_years():
    for year in YEARS:
        all_teams = list_teams(year)
        for my_team in all_teams:
            print(f"Getting data for {my_team}")
            team_name_with_year = f"{my_team['team']}_{my_team['year']}"
            fname = f'raw_data/{team_name_with_year}.html'
            if os.path.exists(fname):
                continue
            html = get_html(my_team['team'], year)
            with open(fname, 'w') as fout:
                fout.write(html)
            time.sleep(0.25)


def list_teams(year):
    params = {
        'y': year,
    }
    response = requests.get('https://kenpom.com/index.php', params=params, cookies=cookies, headers=headers).content
    all_teams = re.findall('team.php.team=.*?"', str(response))[:-1]
    all_teams = [extract_team_and_year(x) for x in all_teams]
    return all_teams


def main():
    if not os.path.exists('raw_data'):
        os.makedirs('raw_data')
    get_data_for_years()


if __name__ == "__main__":
    main()
