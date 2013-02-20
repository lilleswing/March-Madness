for i in 0...15000
	url = "http://www.kenpom.com/player.php?p=#{i}"
	`wget --load-cookies cookies.txt #{url}`
end
