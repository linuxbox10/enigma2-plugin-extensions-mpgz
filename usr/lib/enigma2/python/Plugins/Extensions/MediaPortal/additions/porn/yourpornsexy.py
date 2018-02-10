# -*- coding: utf-8 -*-
###############################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2018
#
#  This plugin is open source but it is NOT free software.
#
#  This plugin may only be distributed to and executed on hardware which
#  is licensed by Dream Property GmbH. This includes commercial distribution.
#  In other words:
#  It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
#  to hardware which is NOT licensed by Dream Property GmbH.
#  It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
#  on hardware which is NOT licensed by Dream Property GmbH.
#
#  This applies to the source code as a whole as well as to parts of it, unless
#  explicitely stated otherwise.
#
#  If you want to use or modify the code or parts of it,
#  you have to keep OUR license and inform us about the modifications, but it may NOT be
#  commercially distributed other than under the conditions noted above.
#
#  As an exception regarding execution on hardware, you are permitted to execute this plugin on VU+ hardware
#  which is licensed by satco europe GmbH, if the VTi image is used on that hardware.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#  For other uses, permission from the authors is necessary.
#
###############################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36'
json_headers = {
	'Accept':'application/json',
	'Accept-Language':'de,en-US;q=0.7,en;q=0.3',
	'X-Requested-With':'XMLHttpRequest',
	'Content-Type':'application/x-www-form-urlencoded',
	}

uid = ''

class YourPornSexyGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("YourPornSexy")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://yourporn.sexy"
		twAgentGetPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		usss = re.findall('usss\[0\] = "(.*?)";', data, re.S)
		if usss:
			global uid
			uid = usss[0]
		parse = re.search('<span>Popular HashTags</span>(.*?)<div class="spacer" style="clear: both;">', data, re.S)
		Cats = re.findall('<a\shref=[\'|"](/blog/.*?)[\'|"].*?<span>#(.*?)</span>', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = "http://yourporn.sexy" + Url.replace('/0.html','/%s.html')
				Title = Title.lower().title()
				self.genreliste.append((Title, Url))
			self.genreliste.sort()
		self.genreliste.insert(0, ("Trends", "http://yourporn.sexy/searches/%s.html"))
		self.genreliste.insert(0, ("Orgasmic", "http://yourporn.sexy/orgasm/"))
		self.genreliste.insert(0, ("Pornstars", "http://yourporn.sexy/pornstars/%s.html"))
		self.genreliste.insert(0, ("Top Viewed (All Time)", "http://yourporn.sexy/popular/top-viewed.html?p=all"))
		self.genreliste.insert(0, ("Top Viewed (Monthly)", "http://yourporn.sexy/popular/top-viewed.html?p=month"))
		self.genreliste.insert(0, ("Top Viewed (Weekly)", "http://yourporn.sexy/popular/top-viewed.html?p=week"))
		self.genreliste.insert(0, ("Top Viewed (Daily)", "http://yourporn.sexy/popular/top-viewed.html?p=day"))
		self.genreliste.insert(0, ("Top Rated (All Time)", "http://yourporn.sexy/popular/top-rated.html?p=all"))
		self.genreliste.insert(0, ("Top Rated (Monthly)", "http://yourporn.sexy/popular/top-rated.html?p=month"))
		self.genreliste.insert(0, ("Top Rated (Weekly)", "http://yourporn.sexy/popular/top-rated.html?p=week"))
		self.genreliste.insert(0, ("Top Rated (Daily)", "http://yourporn.sexy/popular/top-rated.html?p=day"))
		self.genreliste.insert(0, ("Newest", "http://yourporn.sexy/blog/all/%s.html?fl=all&sm=latest"))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.session.openWithCallback(self.SuchenCallback, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = self.suchString, is_dialog=True, auto_text_init=False, suggest_func=self.getSuggestions)
		elif Name == "Trends":
			self.session.open(YourPornSexyTrendsScreen, Link, Name)
		elif Name == "Pornstars":
			self.session.open(YourPornSexyPornstarsScreen, Link, Name)
		else:
			self.session.open(YourPornSexyFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = self.suchString.replace(' ', '-')
			self.session.open(YourPornSexyFilmScreen, Link, Name)

	def getSuggestions(self, text, max_res):
		url = "http://yourporn.sexy/php/livesearch2.php"
		postdata = {'key': text.replace(' ','-'), 'c':'livesearch', 'uid': uid}
		d = getPage(url, method='POST', postdata=urlencode(postdata), agent=myagent, headers=json_headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, err=True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and type(suggestions) in (str, buffer):
			suggestions = json.loads(suggestions)
			for item in suggestions['searches']:
				li = item['title']
				list.append(str(li))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class YourPornSexyPornstarsScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("YourPornSexy")
		self['ContentTitle'] = Label("Pornstars:")
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 26

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		alfa = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.genreliste = []
		url = self.Link.replace('%s', alfa[self.page-1])
		print url
		getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self['page'].setText(str(self.page) + '/' +str(self.lastpage))
		Cats = re.findall("<a href='/(.*?).html' title='.*?PornStar Page'><div class='ps_el'>(.*?)</div></a>", data , re.S)
		if Cats:
			for (Url, Title) in Cats:
				self.genreliste.append((Title, Url))
			self.genreliste.sort
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(YourPornSexyFilmScreen, Link, self.Name)

class YourPornSexyTrendsScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("YourPornSexy")
		self['ContentTitle'] = Label("Trends:")
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.genreliste = []
		url = self.Link.replace('%s', str((self.page-1)*150))
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '', 'ctrl_el.*>(\d+)</div')
		Cats = re.findall('<td><a\shref=[\'|"]/(.*?).html[\'|"]\stitle=[\'|"].*?[\'|"]>(.*?)</a></td><td>(\d+)</td><td>(\d+)</td>', data , re.S)
		if Cats:
			for (Url, Title, Frequency, Results) in Cats:
				self.genreliste.append((Title, Url, Frequency, Results))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		freq = self['liste'].getCurrent()[0][2]
		results = self['liste'].getCurrent()[0][3]
		self['name'].setText(title)
		self['handlung'].setText("Frequency: %s\nResults: %s" % (freq, results))

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(YourPornSexyFilmScreen, Link, self.Name)

class YourPornSexyFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"5" : self.keyShowThumb,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("YourPornSexy")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		if self.Name == "Newest":
			count = 20
		else:
			count = 20
		if re.match(".*?Search", self.Name) or self.Name == "Trends" or self.Name == "Pornstars":
			url = "https://yourporn.sexy/%s.html?page=%s" % (self.Link, str((self.page-1)*30))
			getPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)
		elif (re.match(".*?Top Rated", self.Name) or re.match(".*?Top Viewed", self.Name) or self.Name == "Orgasmic") and self.page>1:
			if re.match(".*?Rated", self.Name):
				mode = 'rating'
			elif re.match(".*?Viewed", self.Name):
				mode = 'views'
			else:
				mode = 'orgasmic'
			if re.match(".*?Monthly", self.Name):
				period = 'month'
			elif re.match(".*?Weekly", self.Name):
				period = 'week'
			elif re.match(".*?Daily", self.Name):
				period = 'day'
			else:
				period = 'all'
			urldata = {
				'popular_mode' : mode,
				'popular_source' : 'blogs',
				'popular_off' : str(((self.page-2)*6)+12),
				'period' : period
				}
			url = 'http://yourporn.sexy/php/popular_append.php'
			getPage(url, agent=myagent, method='POST', postdata=urlencode(urldata), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadData).addErrback(self.dataError)
		else:
			url = self.Link.replace('%s', str((self.page-1)*count))
			twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '', 'ctrl_el.*>(\d+)</div')
		if re.match(".*?Top Rated", self.Name) or re.match(".*?Top Viewed", self.Name) or self.Name == "Orgasmic":
			self.lastpage = 999
			self['page'].setText(str(self.page))
		prep = data
		if re.search("</head>(.*?)<span>Other Results</span>", data, re.S):
			preparse = re.search('</head>(.*?)<span>Other Results</span>', data, re.S)
			if preparse:
				prep = preparse.group(1)
		Movies = re.findall("vid_container.*?<img.*?\ssrc='(.*?.jpg)'.*?a\shref='(.*?\.html.*?)'\sclass='tdn'.*?title='(.*?)'(.*?\sviews)", prep, re.S)
		if Movies:
			for (Image, Url, Title, RuntimeAddedViews) in Movies:
				if ("mini_post_player_img" in RuntimeAddedViews) or ("maxi_post_player_img" in RuntimeAddedViews):
					av = re.findall("class='duration_small.*?'>(.*?)</span.*?>([\d|Hour].*?ago|Yesterday|Last month|Last year)\s<strong>.{0,3}</strong>\s(\d+)\sviews", RuntimeAddedViews, re.S)
					if av:
						Runtime = av[0][0]
						Added = av[0][1]
						Views = av[0][2]
					else:
						Runtime = "-"
						Added = "-"
						Views = "-"
					Url = "http://yourporn.sexy" + Url
					if Image.startswith('//'):
						Image = "http:" + Image
					self.filmliste.append((decodeHtml(Title), Url, Image, Views, Runtime, Added))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, '', '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()
		self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		views = self['liste'].getCurrent()[0][3]
		runtime = self['liste'].getCurrent()[0][4]
		added = self['liste'].getCurrent()[0][5]
		self['name'].setText(title)
		self['handlung'].setText("Views: %s\nRuntime: %s\nAdded: %s" % (views, runtime, added))
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.keyLocked = True
		twAgentGetPage(Link, agent=myagent).addCallback(self.getVideoUrl).addErrback(self.dataError)

	def getVideoUrl(self, data):
		videoUrl = re.findall('<source\ssrc="(.*?)"\stype="video/mp4">', data, re.S)
		if not videoUrl:
			videoUrl = re.findall('<video.*?src=[\'|"](.*?.mp4)[\'|"]', data, re.S)
		if videoUrl:
			Title = self['liste'].getCurrent()[0][0]
			url = videoUrl[-1]
			if url.startswith('//'):
				url = "http:" + url
			self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='yourpornsexy')
		self.keyLocked = False