lines = File.open("../data/teams.txt").readlines()
for line in lines
	line.strip!
	url = "http://www.kenpom.com/#{line}"
	for year in 2003..2012
		url2 = "#{url}&y=#{year}"
		puts url2
		`wget --load-cookies cookies.txt #{url2}`
	end
end
