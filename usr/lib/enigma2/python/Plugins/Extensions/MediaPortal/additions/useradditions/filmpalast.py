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
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

BASEURL = 'http://filmpalast.to'

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

def fp_grabpage(pageurl, method='GET', postdata={}, headers={}):
	if requestsModule:
		try:
			import urlparse
			s = requests.session()
			url = urlparse.urlparse(pageurl)
			if method == 'GET':
				page = s.get(url.geturl())
			elif method == 'POST':
				page = s.post(url.geturl(), data=postdata, headers=headers)
			return page.content
		except:
			pass

class filmPalastMain(MPScreen):

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

		self['title'] = Label("FilmPalast.to")
		self['ContentTitle'] = Label(_("Genre Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.suchString = ''
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("--- Search ---", "callSuchen"))
		self.streamList.append(("Neueste Filme", "/movies/new/page/"))
		self.streamList.append(("Neueste Episoden", "/serien/view/page/"))
		self.streamList.append(("Serien", "/serien/view/"))
		self.streamList.append(("Abenteuer", "/search/genre/Abenteuer/"))
		self.streamList.append(("Action", "/search/genre/Action/"))
		self.streamList.append(("Adventure", "/search/genre/Adventure/"))
		self.streamList.append(("Animation", "/search/genre/Animation/"))
		self.streamList.append(("Biographie", "/search/genre/Biographie/"))
		self.streamList.append(("Comedy", "/search/genre/Comedy/"))
		self.streamList.append(("Crime", "/search/genre/Crime/"))
		self.streamList.append(("Documentary", "/search/genre/Documentary/"))
		self.streamList.append(("Drama", "/search/genre/Drama/"))
		self.streamList.append(("Familie", "/search/genre/Familie/"))
		self.streamList.append(("Fantasy", "/search/genre/Fantasy/"))
		self.streamList.append(("History", "/search/genre/History/"))
		self.streamList.append(("Horror", "/search/genre/Horror/"))
		self.streamList.append(("Komödie", "/search/genre/Kom%C3%B6die/"))
		self.streamList.append(("Krieg", "/search/genre/Krieg/"))
		self.streamList.append(("Krimi", "/search/genre/Krimi/"))
		self.streamList.append(("Musik", "/search/genre/Musik/"))
		self.streamList.append(("Mystery", "/search/genre/Mystery/"))
		self.streamList.append(("Romanze", "/search/genre/Romanze/"))
		self.streamList.append(("Sci-Fi", "/search/genre/Sci-Fi/"))
		self.streamList.append(("Sport", "/search/genre/Sport/"))
		self.streamList.append(("Thriller", "/search/genre/Thriller/"))
		self.streamList.append(("Western", "/search/genre/Western/"))
		self.streamList.append(("Zeichentrick", "/search/genre/Zeichentrick/"))
		self.streamList.append(("0-9", "/search/alpha/0-9/"))
		for c in xrange(26):
			self.streamList.append((chr(ord('A') + c), '/search/alpha/' + chr(ord('A') + c) + '/'))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			Link = "%s/search/title/%s/" % (BASEURL, callback.replace(' ', '%20'))
			Name = self['liste'].getCurrent()[0][0]
			self.session.open(filmPalastParsing, Name, Link)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = BASEURL + self['liste'].getCurrent()[0][1]
		if auswahl == "--- Search ---":
			self.suchen()
		elif auswahl == "Serien":
			self.session.open(filmPalastSerieParsing, auswahl, url)
		else:
			self.session.open(filmPalastParsing, auswahl, url)

class filmPalastSerieParsing(MPScreen, ThumbsHelper):

	def __init__(self, session, genre, url):
		self.genre = genre
		self.url = url
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

		self['title'] = Label("FilmPalast.to")
		self['ContentTitle'] = Label("%s" % self.genre)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		if not mp_globals.requests:
			twAgentGetPage(self.url).addCallback(self.parseData).addErrback(self.dataError)
		else:
			data = fp_grabpage(self.url)
			self.parseData(data)

	def parseData(self, data):
		raw = re.findall('<section id="serien">(.*?)</section>', data, re.S)
		if raw:
			serien = re.findall('<a href="(%s/movies/view/.*?)">(.*?)<' % BASEURL, raw[0])
			if serien:
				for url,title in serien:
					self.streamList.append((decodeHtml(title), url))
		if len(self.streamList) == 0:
			self.streamList.append((_('No movies found!'), ''))
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, 1, 1)
		self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		url = self['liste'].getCurrent()[0][1]
		coverUrl = url.replace('%smovies/view/' % BASEURL, '%s/files/movies/450/' % BASEURL) + '.jpg'
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		self.session.open(filmPalastEpisodenParsing, stream_name, url)

class filmPalastEpisodenParsing(MPScreen, ThumbsHelper):

	def __init__(self, session, genre, url):
		self.genre = genre
		self.url = url
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

		self['title'] = Label("FilmPalast.to")
		self['ContentTitle'] = Label(_("Episode Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		if not mp_globals.requests:
			twAgentGetPage(self.url).addCallback(self.parseData).addErrback(self.dataError)
		else:
			data = fp_grabpage(self.url)
			self.parseData(data)

	def parseData(self, data):
		episoden = re.findall('<a id="staffId_" href="(%s/movies/view/.*?)" class="getStaffelStream".*?</i>(.*?)&' % BASEURL, data, re.S)
		if episoden:
			for (url, title) in episoden:
				cover = url.replace('%s/movies/view/' % BASEURL, '%s/files/movies/450/' % BASEURL) + '.jpg'
				self.streamList.append((decodeHtml(title), url, cover))
		if len(self.streamList) == 0:
			self.streamList.append((_('No movies found!'), '', ''))
		self.streamList.sort()
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, 1, 1)
		self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(filmPalastStreams, stream_name, url, cover)

class filmPalastParsing(MPScreen, ThumbsHelper):

	def __init__(self, session, genre, url):
		self.genre = genre
		self.url = url
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

		self['title'] = Label("FilmPalast.to")
		self['ContentTitle'] = Label("%s" % self.genre)

		self['Page'] = Label(_("Page:"))

		self.page = 1
		self.lastpage = 1
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = self.url+str(self.page)
		if not mp_globals.requests:
			twAgentGetPage(url).addCallback(self.parseData).addErrback(self.dataError)
		else:
			data = fp_grabpage(url)
			self.parseData(data)

	def parseData(self, data):
		self.getLastPage(data, 'id="paging">(.*?)</div>')
		movies = re.findall('<a href="(%s/.*?)" title="(.*?)"> <img src="(.*?.jpg)"' % BASEURL, data)
		if movies:
			for (Url, Title, Image) in movies:
				Image = "http://www.filmpalast.to" + Image
				self.streamList.append((decodeHtml(Title), Url, Image))
		if len(self.streamList) == 0:
			self.streamList.append((_('No movies found!'), None, None))
		else:
			self.keyLocked = False
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.ml.moveToIndex(0)
		self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, self.page, self.lastpage)
		self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		if self.genre == "Neueste Episoden":
			self.session.open(filmPalastEpisodenParsing, stream_name, url)
		else:
			self.session.open(filmPalastStreams, stream_name, url, cover)

class filmPalastStreams(MPScreen):

	def __init__(self, session, stream_name, url, cover):
		self.stream_name = stream_name
		self.url = url
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("FilmPalast.to")
		self['ContentTitle'] = Label(_("Stream Selection"))
		self['name'] = Label(self.stream_name)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		if not mp_globals.requests:
			twAgentGetPage(self.url).addCallback(self.parseData).addErrback(self.dataError)
		else:
			data = fp_grabpage(self.url)
			self.parseData(data)

	def parseData(self, data):
		self.streamList = []
		streams = re.findall('currentStreamLinks.*?class="hostName">(.*?)<.*?data-id="(.*?)"', data, re.S)
		if streams:
			for (Hoster, UrlID) in streams:
					if isSupportedHoster(Hoster, True):
						self.streamList.append((Hoster, UrlID))
		if len(self.streamList) == 0:
			self.streamList.append((_('No supported streams found!'), None))
		self.ml.setList(map(self._defaultlisthoster, self.streamList))
		CoverHelper(self['coverArt']).getCover(self.cover)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		urlId = self['liste'].getCurrent()[0][1]
		if urlId:
			url = "%s/stream/%s/1" % (BASEURL, urlId)
			IDdata = {'streamID': urlId}
			if not mp_globals.requests:
				twAgentGetPage(url, method='POST', postdata=urlencode(IDdata), headers={'Accept':'*/*', 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'}).addCallback(self.get_stream).addErrback(self.dataError)
			else:
				data = fp_grabpage(url, method='POST', postdata=IDdata, headers={'Accept':'*/*', 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest'})
				self.get_stream(data)

	def get_stream(self, data):
		streams = re.search('"url":"(.*?)"', data, re.S)
		if streams:
			get_stream_link(self.session).check_link(streams.group(1).replace('\/','/'), self.playfile)
		else:
			message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def playfile(self, stream_url):
		self.session.open(SimplePlayer, [(self.stream_name, stream_url, self.cover)], showPlaylist=False, ltype='filmpalast', cover=True)