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

try:
	from Plugins.Extensions.MediaPortal.resources import cfscrape
except:
	cfscrapeModule = False
else:
	cfscrapeModule = True

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

import urlparse
import thread

kx_url = 'http://kinox.to'
kx_cookies = CookieJar()
kx_ck = {}
kx_agent = ''

class kxGenre(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(_("Genre Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		thread.start_new_thread(self.get_tokens,("GetTokens",))
		self['name'].setText(_("Please wait..."))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global kx_ck
			global kx_agent
			if kx_ck == {} or kx_agent == '':
				kx_ck, kx_agent = cfscrape.get_tokens(kx_url)
				requests.cookies.cookiejar_from_dict(kx_ck, cookiejar=kx_cookies)
			else:
				s = requests.session()
				url = urlparse.urlparse(kx_url)
				headers = {'user-agent': kx_agent}
				page = s.get(url.geturl(), cookies=kx_cookies, headers=headers, allow_redirects=False)
				if page.status_code == 503 and page.headers.get("Server") == "cloudflare-nginx":
					kx_ck, kx_agent = cfscrape.get_tokens(kx_url)
					requests.cookies.cookiejar_from_dict(kx_ck, cookiejar=kx_cookies)
			self.keyLocked = False
			reactor.callFromThread(self.getGenres)
		else:
			reactor.callFromThread(self.kx_error)

	def kx_error(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or python-pyexecjs and nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def getGenres(self):
		self.currentdatum = strftime("%d.%m.%Y", localtime())
		self.keyLocked = True
		date = datetime.datetime.now().strftime('%Y-%m-%d')
		self.streamList.append(("Frisches aus dem Kino vom %s" % self.currentdatum, "http://kinox.to/index.php"))
		self.streamList.append(("Neue Filme online vom %s" % self.currentdatum, "http://kinox.to/index.php"))
		self.streamList.append(("Kinofilme", "http://kinox.to/Kino-filme.html"))
		self.streamList.append(("Suche", "dump"))
		self.streamList.append(("Filme A-Z", "dump"))
		self.streamList.append(("Neueste Filme", "http://kinox.to/Latest-Movies.html"))
		self.streamList.append(("Beliebte Filme", "http://kinox.to/Popular-Movies.html"))
		self.streamList.append(("Serien A-Z","dump"))
		self.streamList.append(("Neueste Serien", "http://kinox.to/Latest-Series.html"))
		self.streamList.append(("Beliebte Serien", "http://kinox.to/Popular-TVSeries.html"))
		self.streamList.append(("Dokumentationen A-Z","dump"))
		self.streamList.append(("Neueste Dokumentationen", "http://kinox.to/Latest-Documentations.html"))
		self.streamList.append(("Beliebte Dokumentationen", "http://kinox.to/Popular-Documentations.html"))
		self.streamList.append(("Watchlist","dump"))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		if auswahl == "Kinofilme":
			self.session.open(kxKino, url)
		elif "Neue Filme online vom" in auswahl:
			self.session.open(kxNeuesteOnline, url)
		elif "Frisches aus dem Kino vom" in auswahl:
			self.session.open(kxNeuesteKino, url)
		elif "Neueste" in auswahl:
			self.session.open(kxNeueste, url, auswahl)
		elif "Beliebte" in auswahl:
			self.session.open(kxNeueste, url, auswahl)
		elif "A-Z" in auswahl:
			self.session.open(kxABC, url, auswahl)
		elif auswahl == "Suche":
			self.session.openWithCallback(self.searchCallback, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = "", is_dialog=True, auto_text_init=True)
		elif auswahl == "Watchlist":
			self.session.open(kxWatchlist)

	def searchCallback(self, callbackStr):
		if callbackStr is not None:
			self.searchStr = callbackStr
			url = "http://kinox.to/Search.html?q="
			self.searchData = self.searchStr
			self.session.open(kxSucheScreen, url, self.searchData)

class kxKino(MPScreen, ThumbsHelper):

	def __init__(self, session, kxGotLink):
		self.kxGotLink = kxGotLink
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label("Kinofilme")

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		kxMovies = re.findall('<div class="Opt leftOpt Headlne"><a title=".*?" href="(.*?)"><h1>(.*?)</h1></a></div>.*?<div class="Thumb"><img style="width: 70px; height: 100px" src="(.*?)"\s{0,2}/></div>.*?<div class="Descriptor">(.*?)</div>.*?src="/gr/sys/lng/(.*?).png"', data, re.S)
		if kxMovies:
			for (kxUrl,kxTitle,kxImage,kxHandlung,kxLang) in kxMovies:
				kxUrl = "http://kinox.to" + kxUrl
				kxImage = "http://kinox.to"+ kxImage
				self.streamList.append((decodeHtml(kxTitle),kxUrl,kxImage,kxLang,kxHandlung))
			self.ml.setList(map(self.kinoxlistleftflagged, self.streamList))
			self.keyLocked = False
			self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, 1, 1)
			self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		coverUrl = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][4]
		self['handlung'].setText(decodeHtml(handlung))
		CoverHelper(self['coverArt']).getCover(coverUrl, agent=kx_agent, cookieJar=kx_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(kxStreams, auswahl, stream_name, cover)

class kxNeuesteKino(MPScreen, ThumbsHelper):

	def __init__(self, session, kxGotLink):
		self.kxGotLink = kxGotLink
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		lt = localtime()
		self.currentdatum = strftime("%d.%m.%Y", lt)
		self['ContentTitle'] = Label("Frisches aus dem Kino vom %s" % self.currentdatum)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw_m = re.findall('<div class="Opt leftOpt Headlne"><h1>Frisches aus dem Kino(.*?)</table>', data, re.S)
		if raw_m:
			movies = re.findall('td class="Title img_preview" rel="(.*?)"><a href="(/Stream/.*?)" title=".*?" class="OverlayLabel">(.*?)</a></td>', raw_m[0], re.S)
			if movies:
				for (kxImage,kxUrl,kxTitle) in movies:
					kxUrl = "http://kinox.to" + kxUrl
					kxImage = "http://kinox.to"+ kxImage
					self.streamList.append((decodeHtml(kxTitle),kxUrl,kxImage))
				self.ml.setList(map(self._defaultlistleft, self.streamList))
				self.keyLocked = False
				self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, 1, 1)
				self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(image, agent=kx_agent, cookieJar=kx_cookies)

	def getDetails(self, data):
		details = re.findall('<div class="Grahpics">.*?<img src="(.*?)".*?<div class="Descriptore">(.*?)</div>', data, re.S)
		if details:
			for (image, handlung) in details:
				self['handlung'].setText(decodeHtml(handlung))
				CoverHelper(self['stationIcon']).getCover(image, agent=kx_agent, cookieJar=kx_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(kxStreams, auswahl, stream_name, cover)

class kxNeuesteOnline(MPScreen, ThumbsHelper):

	def __init__(self, session, kxGotLink):
		self.kxGotLink = kxGotLink
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		lt = localtime()
		self.currentdatum = strftime("%d.%m.%Y", lt)
		self['ContentTitle'] = Label("Neue Filme online vom %s" % self.currentdatum)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		neueste = re.findall('div class="Opt leftOpt Headlne"><h1>Neue Filme online vom(.*?)</table>', data, re.S)
		if neueste:
			movies = re.findall('td class="Title img_preview" rel="(.*?)"><a href="(/Stream/.*?)" title=".*?" class="OverlayLabel">(.*?)</a></td>', neueste[0], re.S)
			if movies:
				for (kxImage,kxUrl,kxTitle) in movies:
					kxUrl = "http://kinox.to" + kxUrl
					kxImage = "http://kinox.to"+ kxImage
					self.streamList.append((decodeHtml(kxTitle),kxUrl,kxImage))
					self.ml.setList(map(self._defaultlistleft, self.streamList))
				self.keyLocked = False
				self.th_ThumbsQuery(self.streamList, 0, 1, None, None, '<div class="Grahpics">.*?<img src="(.*?)"', 1, 1)
				self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(image, agent=kx_agent, cookieJar=kx_cookies)
		getPage(url, agent=kx_agent, cookies=kx_ck).addCallback(self.getDetails).addErrback(self.dataError)

	def getDetails(self, data):
		details = re.findall('<div class="Grahpics">.*?<img src="(.*?)".*?<div class="Descriptore">(.*?)</div>', data, re.S)
		if details:
			for (image, handlung) in details:
				image = "http://kinox.to"+ image
				self['handlung'].setText(decodeHtml(handlung))
				#CoverHelper(self['coverArt']).getCover(image)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		self.session.open(kxStreams, auswahl, stream_name, None)

class kxABC(MPScreen):

	def __init__(self, session, kxGotLink, name):
		self.kxGotLink = kxGotLink
		self.Name = name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(self.Name)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		abc = ["#","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
		for letter in abc:
			self.streamList.append((letter, ''))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		self.session.open(kxABCpage, auswahl, self.Name.replace('A-Z',''))

class kxABCpage(MPScreen, ThumbsHelper):

	def __init__(self, session, letter, name):
		self.letter = letter
		self.Name = name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		if "Serien" in self.Name:
			self["actions2"] = ActionMap(["MP_Actions"], {
				"green" : self.keyAdd
			}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(self.Name + self.letter)
		if "Serien" in self.Name:
			self['F2'] = Label(_("Add to Watchlist"))

		self['Page'] = Label(_("Page:"))
		self['page'] = Label("1")

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.page = 1
		self.lastpage = 999
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if "Serien" in self.Name:
			type = "series"
		elif "Filme" in self.Name:
			type = "movie"
		else:
			type = "documentation"
		self.streamList = []
		if self.letter == "#":
			letter = "1"
		else:
			letter = "%22"+self.letter+"%22"
		url = "http://kinox.to/aGET/List/?sEcho=1&iColumns=7&sColumns=&iDisplayStart="+str((self.page-1)*25)+"&iDisplayLength=25&iSortingCols=1&iSortCol_0=2&sSortDir_0=asc&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=false&bSortable_4=false&bSortable_5=false&bSortable_6=true&additional=%7B%22fType%22%3A%22"+type+"%22%2C%22Length%22%3A30%2C%22fLetter%22%3A"+letter+"%7D"
		getPage(url, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		data = data.replace('\\/','/').replace('\\"','"')
		kxMovies = re.findall('\["(\d+)".*?href="(.*?)".*?">(.*?)</a>.*?class="Year">(.*?)</span>', data, re.S)
		if kxMovies:
			for (kxLang,kxUrl,kxTitle,Year) in kxMovies:
				kxUrl = "http://kinox.to" + kxUrl
				kxImage = None
				kxHandlung = ""
				kxTitle = kxTitle + " (" + Year + ")"
				self.streamList.append((decodeHtml(kxTitle),kxUrl,kxImage,kxLang,kxHandlung))
				self.ml.setList(map(self.kinoxlistleftflagged, self.streamList))
			self.keyLocked = False
			self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, self.page)
			self.showInfos()
		else:
			self['page'].setText("END")

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		self['page'].setText(str(self.page))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		if "Serien" in self.Name:
			self.session.open(kxEpisoden, auswahl, stream_name)
		else:
			self.session.open(kxStreams, auswahl, stream_name, None)

	def keyAdd(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		muTitle = self['liste'].getCurrent()[0][0]
		muID = self['liste'].getCurrent()[0][1]
		muLang = self['liste'].getCurrent()[0][3]
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			writePlaylist = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","a")
			writePlaylist.write('"%s" "%s" "%s" "0"\n' % (muTitle, muID, muLang))
			writePlaylist.close()
			message = self.session.open(MessageBoxExt, _("Selection was added to the watchlist."), MessageBoxExt.TYPE_INFO, timeout=3)

class kxNeueste(MPScreen, ThumbsHelper):

	def __init__(self, session, kxGotLink, name):
		self.kxGotLink = kxGotLink
		self.Name = name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		if "Serien" in self.Name:
			self["actions2"] = ActionMap(["MP_Actions"], {
				"green" : self.keyAdd
			}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(self.Name)
		self['name'] = Label(_("Selection:"))
		if "Serien" in self.Name:
			self['F2'] = Label(_("Add to Watchlist"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		kxMovies = re.findall('<td class="Icon"><img width="16" height="11" src="/gr/sys/lng/(.*?).png" alt="language"></td>.*?<td class="Title"><a href="(.*?)" onclick="return false;">(.*?)</a>', data, re.S)
		if kxMovies:
			for (kxLang,kxUrl,kxTitle) in kxMovies:
				kxUrl = "http://kinox.to" + kxUrl
				self.streamList.append((decodeHtml(kxTitle),kxUrl,'',kxLang))
				self.ml.setList(map(self.kinoxlistleftflagged, self.streamList))
			self.keyLocked = False
			self.th_ThumbsQuery(self.streamList, 0, 1, None, 2, '<div class="Grahpics">.*?<img src="(.*?)"', 1, 1)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		if "Serien" in self.Name:
			self.session.open(kxEpisoden, auswahl, stream_name)
		else:
			self.session.open(kxStreams, auswahl, stream_name, None)

	def keyAdd(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		muTitle = self['liste'].getCurrent()[0][0]
		muID = self['liste'].getCurrent()[0][1]
		muLang = self['liste'].getCurrent()[0][3]

		if not fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			writePlaylist = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","a")
			writePlaylist.write('"%s" "%s" "%s" "0"\n' % (muTitle, muID, muLang))
			writePlaylist.close()
			message = self.session.open(MessageBoxExt, _("Selection was added to the watchlist."), MessageBoxExt.TYPE_INFO, timeout=3)

class kxEpisoden(MPScreen):

	def __init__(self, session, url, stream_name):
		self.url = url
		self.stream_name = stream_name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(_("Episode Selection"))
		self['name'] = Label(self.stream_name)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.url, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.watched_liste = []
		self.mark_last_watched = []
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watched"):
			open(config.mediaportal.watchlistpath.value+"mp_kx_watched","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watched"):
			leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_kx_watched")
			if not leer == 0:
				self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_kx_watched" , "r")
				for lines in sorted(self.updates_read.readlines()):
					line = re.findall('"(.*?)"', lines)
					if line:
						self.watched_liste.append("%s" % (line[0]))
				self.updates_read.close()
		MirrorByEpisode = "http://kinox.to/aGET/MirrorByEpisode/"
		if re.match('.*rel="\?Addr=', data, re.S):
			id = re.findall('rel="(\?Addr=.*?)"', data, re.S)
			if id:
				staffeln2 = re.findall('<option value="(.*\d+)" rel="(.*\d+)"', data, re.M)
				if staffeln2:
					for each in staffeln2:
						(staffel, epsall) = each
						eps = re.findall('(\d+)', epsall, re.S)
						for episode in eps:
							url_to_streams = "%s%s&Season=%s&Episode=%s" % (MirrorByEpisode, id[0], staffel, episode)
							if int(staffel) < 10:
								staffel3 = "S0"+str(staffel)
							else:
								staffel3 = "S"+str(staffel)
							if int(episode) < 10:
								episode3 = "E0"+str(episode)
							else:
								episode3 = "E"+str(episode)
							self.staffel_episode = "%s%s" % (staffel3, episode3)
							if self.staffel_episode:
								streamname = "%s - %s" % (self.stream_name, self.staffel_episode)
								if streamname in self.watched_liste:
									self.streamList.append((streamname,url_to_streams,True))
									self.mark_last_watched.append(streamname)
								else:
									self.streamList.append((streamname,url_to_streams,False))
						if len(self.mark_last_watched) != 0:
							counting_watched = 0
							for (name,url,watched) in self.streamList:
								counting_watched += 1
								if self.mark_last_watched[-1] == name:
									counting_watched = int(counting_watched) - 1
									print "[kinox] last watched episode: %s" % counting_watched
									break
							self["liste"].moveToIndex(int(counting_watched))
						else:
							if len(self.streamList) != 0:
								jump_last = len(self.streamList) -1
							else:
								jump_last = 0
							print "[kinox] last episode: %s" % jump_last
							self["liste"].moveToIndex(int(jump_last))
		if len(self.streamList) == 0:
			self.streamList.append((_('No episodes found!'), None, None))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
		else:
			self.keyLocked = False
			self.ml.setList(map(self._defaultlistleftmarked, self.streamList))
		details = re.findall('<div class="Grahpics">.*?<img src="(.*?)".*?<div class="Descriptore">(.*?)</div>', data, re.S)
		if details:
			for (image, handlung) in details:
				image = "http://kinox.to"+ image
				self['handlung'].setText(decodeHtml(stripAllTags(handlung)))
				CoverHelper(self['coverArt']).getCover(image, agent=kx_agent, cookieJar=kx_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		episode = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		streamname = "%s" % episode
		self.session.open(kxStreams, auswahl, streamname, None)

class kxWatchlist(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"red" : self.keyDel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("kinox.to")
		self['ContentTitle'] = Label("Watchlist")
		self['F1'] = Label(_("Delete"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPlaylist)

	def loadPlaylist(self):
		self.streamList = []
		if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			readStations = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","r")
			for rawData in readStations.readlines():
				data = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)"', rawData, re.S)
				if data:
					(stationName, stationLink, stationLang, stationTotaleps) = data[0]
					self.streamList.append((stationName, stationLink, '', stationLang))
			self.streamList.sort()
			readStations.close()
			self.ml.setList(map(self.kinoxlistleftflagged, self.streamList))
		if len(self.streamList) == 0:
			self.streamList.append((_('Watchlist is currently empty'), None))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		auswahl = self['liste'].getCurrent()[0][1]
		if self.keyLocked or not auswahl:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		self.session.open(kxEpisoden, auswahl, stream_name)

	def keyDel(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		selectedName = self['liste'].getCurrent()[0][0]
		writeTmp = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist.tmp","w")
		if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
			readStations = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","r")
			for rawData in readStations.readlines():
				data = re.findall('"(.*?)" "(.*?)" "(.*?)" "(.*?)"', rawData, re.S)
				if data:
					(stationName, stationLink, stationLang, stationTotaleps) = data[0]
					if stationName != selectedName:
						writeTmp.write('"%s" "%s" "%s" "%s"\n' % (stationName, stationLink, stationLang, stationTotaleps))
			readStations.close()
			writeTmp.close()
			shutil.move(config.mediaportal.watchlistpath.value+"mp_kx_watchlist.tmp", config.mediaportal.watchlistpath.value+"mp_kx_watchlist")
			self.loadPlaylist()

class kxStreams(MPScreen):

	def __init__(self, session, kxGotLink, stream_name, cover=None):
		self.kxGotLink = kxGotLink
		self.stream_name = stream_name
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(_("Stream Selection"))
		self['name'] = Label(self.stream_name)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		hosterdump = re.findall('<li id="Hoster(.*?)/li>', data, re.S)
		if hosterdump:
			self.streamList = []
			self.streamList.append(("Hoster", "nix", "Mirror", "Hits", "Date"))
			for each in hosterdump:
				if re.search('Mirror', each, re.I):
					hosters = re.findall('rel="(.*?)".*?<div class="Named">(.*?)</div>.*?<div class="Data"><b>Mirror</b>\:.(.*?)<br.*?><b>Vom</b>\:.(.*\d+)</div>',each, re.S|re.I)
					if hosters:
						(get_stream_url, hostername, mirror, date)= hosters[0]
						mirrors = re.findall('[0-9]/([0-9])', mirror)
						if mirrors:
							print "total", mirrors[0]
							get_stream_url_m = ''
							for i in range(1,int(mirrors[0])+1):
								if re.search('Season=', get_stream_url, re.S):
									details = re.findall('(.*?)&amp;Hoster=(.*?)&amp;Mirror=(.*?)&amp;Season=(.*?)&amp;Episode=(\d+)', get_stream_url, re.S)
									if details:
										(dname, dhoster, dmirror, dseason, depisode) = details[0]
										get_stream_url_m = "http://kinox.to/aGET/Mirror/%s&Hoster=%s&Mirror=%s&Season=%s&Episode=%s" %  (dname, dhoster, str(i), dseason, depisode)
									else:
										details = re.findall('(.*?)&amp;Hoster=(.*?)&amp;Season=(.*?)&amp;Episode=(\d+)', get_stream_url, re.S)
										(dname, dhoster, dseason, depisode) = details[0]
										get_stream_url_m = "http://kinox.to/aGET/Mirror/%s&Hoster=%s&Season=%s&Episode=%s" %  (dname, dhoster, dseason, depisode)
								else:
									details = re.findall('(.*?)&amp;Hoster=(.*?)&amp;Mirror=(\d+)', get_stream_url, re.S)
									if details:
										(dname, dhoster, dmirror) = details[0]
										get_stream_url_m = "http://kinox.to/aGET/Mirror/%s&Hoster=%s&Mirror=%s" %  (dname, dhoster, str(i))
									else:
										details = re.findall('(.*?)&amp;Hoster=(\d+)', get_stream_url, re.S)
										if details:
											(dname, dhoster) = details[0]
											get_stream_url_m = "http://kinox.to/aGET/Mirror/%s&Hoster=%s" %  (dname, dhoster)
								if isSupportedHoster(hostername, True):
									self.streamList.append((hostername, get_stream_url_m, str(i)+"/"+mirrors[0], '', date))
				else:
					hosters = re.findall('rel="(.*?)".*?<div class="Named">(.*?)</div>.*?<div class="Data"><b>Vom</b>\:.(.*\d+)</div>',each, re.S)
					if hosters:
						(get_stream_url, hostername, date)= hosters[0]
						get_stream_url = "http://kinox.to/aGET/Mirror/%s" % get_stream_url.replace('&amp;','&')
						if isSupportedHoster(hostername, True):
							self.streamList.append((hostername, get_stream_url, "1", '', date))
		if len(self.streamList) == 0:
			self.streamList.append((_('No supported streams found!'), None, None, None, None))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
		else:
			self.keyLocked = False
			self.ml.setList(map(self.kxStreamListEntry, self.streamList))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=kx_agent, cookies=kx_ck).addCallback(self.parseStream, url).addErrback(self.dataError)

	def parseStream(self, data, url):
		data = data.replace('\/','/').replace('\\"','"')
		if re.match('.*?Part', data, re.S):
			print "more parts.."
			urls = []
			urls.append(("Part 1", url+"&Part=1"))
			urls.append(("Part 2", url+"&Part=2"))
			self.session.open(kxParts, urls, self.stream_name)
		else:
			print "one parts only.."
			stream = None
			extern_stream_url = re.findall('(?:href|src)="((?:https?:|)//.*?)"', data)
			if extern_stream_url:
				stream = extern_stream_url[0]
				if stream:
					if stream.startswith('//'):
						stream = "http:" + stream
					get_stream_link(self.session).check_link(stream, self.playfile)
			if not stream:
				self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=5)

	def playfile(self, stream_url):
		if stream_url != None:
			if not fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watched"):
				open(config.mediaportal.watchlistpath.value+"mp_kx_watched","w").close()

			self.update_liste = []
			leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_kx_watched")
			if not leer == 0:
				self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_kx_watched" , "r")
				for lines in sorted(self.updates_read.readlines()):
					line = re.findall('"(.*?)"', lines)
					if line:
						self.update_liste.append("%s" % (line[0]))
				self.updates_read.close()

				updates_read2 = open(config.mediaportal.watchlistpath.value+"mp_kx_watched" , "a")
				check = ("%s" % self.stream_name)
				if not check in self.update_liste:
					print "[kinox] update add: %s" % (self.stream_name)
					updates_read2.write('"%s"\n' % (self.stream_name))
					updates_read2.close()
				else:
					print "[kinox] dupe %s" % (self.stream_name)
			else:
				updates_read3 = open(config.mediaportal.watchlistpath.value+"mp_kx_watched" , "a")
				print "[kinox] update add: %s" % (self.stream_name)
				updates_read3.write('"%s"\n' % (self.stream_name))
				updates_read3.close()

			self.session.open(SimplePlayer, [(self.stream_name, stream_url, self.cover)], showPlaylist=False, ltype='kinox.to', cover=True)

class kxParts(MPScreen):

	def __init__(self, session, parts, stream_name):
		self.parts = parts
		self.stream_name = stream_name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label(_("Parts Selection"))
		self['name'] = Label(self.stream_name)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		for (partName, partUrl) in self.parts:
			self.streamList.append((partName, partUrl))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		data = data.replace('\/','/').replace('\\"','"')
		extern_stream_url = re.findall('(?:href|src)="(http.*?)"', data, re.S)
		stream = None
		if extern_stream_url:
			stream = extern_stream_url[0]
			if stream:
				get_stream_link(self.session).check_link(stream, self.playfile)
		if not stream:
			self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=5)

	def playfile(self, stream_url):
		if stream_url != None:
			part = self['liste'].getCurrent()[0][0]
			streamname = "%s - %s" % (self.stream_name ,part)
			self.session.open(SimplePlayer, [(streamname, stream_url)], showPlaylist=False, ltype='kinox.to', cover=False)

class kxSucheScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, searchURL, searchData):
		self.kxGotLink = searchURL + searchData
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"green" : self.keyAdd
		}, -1)

		self['title'] = Label("Kinox.to")
		self['ContentTitle'] = Label("Suche nach Filmen")
		self['F2'] = Label(_("Add to Watchlist"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		if requestsModule and cfscrapeModule:
			self.streamList = []
			getPage(self.kxGotLink, agent=kx_agent, cookies=kx_ck).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		movies = re.findall('<td\sclass="Icon"><img\swidth="16"\sheight="11"\ssrc="/gr/sys/lng/(.*?).png"\salt="language"></td>.*?title="(.*?)".*?<td\sclass="Title">(.*?)>(.*?)</a>', data, re.S)
		if movies:
			for (kxLang,kxArt,kxUrl,kxTitle) in movies:
				kxUrl = re.search('href="(.*?)"', kxUrl, re.S).group(1)
				if kxUrl != '':
					kxUrl = "http://kinox.to" + kxUrl
					if kxArt == 'documentation':
						kxArt = 'doku'
					self.streamList.append((decodeHtml(kxTitle),kxUrl, kxLang, kxArt.capitalize()))
			self.ml.setList(map(self.kxListSearchEntry, self.streamList))
			self.keyLocked = False
			self.th_ThumbsQuery(self.streamList, 0, 1, None, 2, '<div class="Grahpics">.*?<img src="(.*?)"', 1, 1)
			self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=kx_agent, cookies=kx_ck).addCallback(self.getDetails).addErrback(self.dataError)

	def getDetails(self, data):
		details = re.findall('<div class="Grahpics">.*?<img src="(.*?)".*?<div class="Descriptore">(.*?)</div>', data, re.S)
		if details:
			for (image, handlung) in details:
				image = "http://kinox.to"+ image
				self['handlung'].setText(decodeHtml(handlung))
				CoverHelper(self['coverArt']).getCover(image, agent=kx_agent, cookieJar=kx_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		art = self['liste'].getCurrent()[0][3]
		if art == 'Series':
			self.session.open(kxEpisoden, auswahl, stream_name)
		else:
			self.session.open(kxStreams, auswahl, stream_name, None)

	def keyAdd(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		art = self['liste'].getCurrent()[0][3]
		if art == 'Series':
			if not fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
				open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","w").close()
			if fileExists(config.mediaportal.watchlistpath.value+"mp_kx_watchlist"):
				writePlaylist = open(config.mediaportal.watchlistpath.value+"mp_kx_watchlist","a")
				writePlaylist.write('"%s" "%s" "%s" "0"\n' % (stream_name, url, "1")) # default German language
				writePlaylist.close()
				message = self.session.open(MessageBoxExt, _("Selection was added to the watchlist."), MessageBoxExt.TYPE_INFO, timeout=3)