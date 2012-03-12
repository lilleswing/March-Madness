datapath=~/Documents/CompSci/March_Madness/data


mkdir "$datapath/team_data"
mkdir "$datapath/player_data"
mkdir "$datapath/stat_data"
mkdir "$datapath/stat_data/height"
mkdir "$datapath/stat_data/stats"
mkdir "$datapath/stat_data/summary"
mkdir "$datapath/stat_data/teamstats"
mkdir "$datapath/team_csv"
mkdir "$datapath/player_csv"
mkdir "$datapath/sta_csv"



python get_team_names.py
ruby get_team_data.rb
mv *team=* "$datapath/team_data"
ruby get_player_data.rb
mv *team=* "$datapath/player_data"
ruby get_stats.rb
mv height* "$datapath/stat_data/height"
mv stats* "$datapath/stat_data/stats"
mv summary* "$datapath/stat_data/summary"
mv teamstats* "$datapath/stat_data/teamstats"
python parse_player_data.py "$datapath/player_data"
python parse_team_data.py "$datapath/team_data"
python parse_stat_data.py "$datapath/stat_data/height" 9 "height"
python parse_stat_data.py "$datapath/stat_data/teamstats" 7 "teamstats"
python parse_stat_data.py "$datapath/stat_data/summary" 6 "summary"
python parse_stat_data.py "$datapath/stat_data/stats" 11 "stats"


