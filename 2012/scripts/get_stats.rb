stats = ["height.php?","teamstats.php?","summary.php?","stats.php?"]
for stat in stats
	for year in 2003..2012
		url = "http://www.kenpom.com/#{stat}y=#{year}"
		`wget --load-cookies cookies.txt #{url}`
	end
end
