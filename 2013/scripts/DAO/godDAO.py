__author__ = 'karl_leswing'
#tables
#games
#   year, team1, team2, value

#teams
#   year, name, [stats]
#   I HOPE TO GOD [stats] ARE IN THE SAME ORDER YEAR TO YEAR

#avg points
#   year, team, points_for, points_against
import sqlite3


def create_tables():
    sql = 'create table if not exists games (year INTEGER, team1 TEXT, team2 TEXT, value REAL,\
     PRIMARY KEY (year, team1, team2))'
    curr.execute(sql)
    sql = 'create table if not exists teams (year INTEGER, name TEXT, s1 REAL,s2 REAL,s3 REAL,s4 REAL,s5 REAL,s6 REAL,\
    s7 REAL,s8 REAL,s9 REAL,s10 REAL,s11 REAL,s12 REAL,s13 REAL,s14 REAL,s15 REAL,s16 REAL,s17 REAL,s18 REAL,s19 REAL\
    ,s20 REAL,s21 REAL,s22 REAL,s23 REAL,s24 REAL,s25 REAL,s26 REAL,s27 REAL,s28 REAL,s29 REAL,s30 REAL,\
     PRIMARY KEY (year, name))'
    curr.execute(sql)
    sql = 'create table if not exists avgpoints (year INTEGER, team TEXT, points_for REAL, points_against REAL,\
     PRIMARY KEY(year, team))'
    curr.execute(sql)
    conn.commit()


def get_avgpoints():
    teams = dict()
    curr.execute('SELECT * from avgpoints')
    for team in curr:
        teams[(team[0], team[1])] = team[2:]
    return teams


def get_games():
    curr.execute('SELECT * from games')
    return map(lambda x: [(x[0], x[1]), (x[0], x[2]), x[3]], curr.fetchall())


def get_teams():
    teams = dict()
    curr.execute('SELECT * from teams')
    for team in curr:
        teams[(team[0], team[1])] = team[2:]
    return teams


def add_avgpoints(year, avgpoints):
    avgpoints = ([year] + avgpoints)
    curr.execute('INSERT OR REPLACE INTO avgpoints VALUES (?,?,?,?)', avgpoints)
    conn.commit()


def add_games(year, games):
    games = map(lambda x: tuple([year] + x), games)
    curr.executemany('INSERT OR REPLACE INTO games VALUES (?,?,?,?)', games)
    conn.commit()


def add_team(year, name, data):
    vars = tuple([year] + [name] + data)
    curr.execute('INSERT OR REPLACE INTO teams VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', vars)
    conn.commit()

conn = sqlite3.connect('../data/kenpom.db')
curr = conn.cursor()
create_tables()
