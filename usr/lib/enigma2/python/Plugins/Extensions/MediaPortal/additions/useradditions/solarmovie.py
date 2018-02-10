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

BASE_URL = 'http://www.solarmovie.fm/'

class solarMovieMain(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("SolarMovie")
		self['ContentTitle'] = Label("Choose Genre:")

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("Latest", "/?page="))
		self.streamList.append(("Action", "/?genre=Action&page="))
		self.streamList.append(("Musical", "/?genre=Musical&page="))
		self.streamList.append(("Mystery", "/?genre=Mystery&page="))
		self.streamList.append(("Reality-TV", "/?genre=Reality-TV&page="))
		self.streamList.append(("Romance", "/?genre=Romance&page="))
		self.streamList.append(("Sci-Fi", "/?genre=Sci-Fi&page="))
		self.streamList.append(("Short", "/?genre=Short&page="))
		self.streamList.append(("Sport", "/?genre=Sport&page="))
		self.streamList.append(("Talk-Show", "/?genre=Talk-Show&page="))
		self.streamList.append(("Thriller", "/?genre=Thriller&page="))
		self.streamList.append(("War", "/?genre=War&page="))
		self.streamList.append(("Western", "/?genre=Western&page="))
		self.streamList.append(("Zombies", "/?genre=Zombies&page="))
		self.streamList.append(("Music", "/?genre=Music&page="))
		self.streamList.append(("Korean", "/?genre=Korean&page="))
		self.streamList.append(("Animation", "/?genre=Animation&page="))
		self.streamList.append(("Biography", "/?genre=Biography&page="))
		self.streamList.append(("Comedy", "/?genre=Comedy&page="))
		self.streamList.append(("Crime", "/?genre=Crime&page="))
		self.streamList.append(("Documentary", "/?genre=Documentary&page="))
		self.streamList.append(("Drama", "/?genre=Drama&page="))
		self.streamList.append(("Family", "/?genre=Family&page="))
		self.streamList.append(("Fantasy", "/?genre=Fantasy&page="))
		self.streamList.append(("Game-Show", "/?genre=Game-Show&page="))
		self.streamList.append(("History", "/?genre=History&page="))
		self.streamList.append(("Horror", "/?genre=Horror&page="))
		self.streamList.append(("Japanese", "/?genre=Japanese&page="))
		self.streamList.append(("Adventure", "/?genre=Adventure&page="))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = BASE_URL + self['liste'].getCurrent()[0][1]
		self.session.open(solarMovieParsing, auswahl, url)

class solarMovieParsing(MPScreen, ThumbsHelper):

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

		self['title'] = Label("SolarMovie")
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
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, 'class="pagination"(.*?)</div>', '(\d+)">>>')
		movies = re.findall('class="ml-item".*?href="(.*?)".*?\salt="(.*?)"\ssrc="(.*?)"', data, re.S)
		if movies:
			for (Url, Title, Image) in movies:
				self.streamList.append((decodeHtml(Title), Url, Image))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.ml.moveToIndex(0)
			self.keyLocked = False
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
		movie_url = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(solarMovieStreams, stream_name, movie_url, cover)

class solarMovieStreams(MPScreen):

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

		self['title'] = Label("SolarMovie")
		self['ContentTitle'] = Label("Streams:")

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.streamList = []
		streams = re.findall('server_servername">(.*?)</.*?server_play.*?href="(.*?)"', data, re.S)
		if streams:
			for (Hoster, Url) in streams:
				if isSupportedHoster(Hoster, True):
					self.streamList.append((Hoster, Url))
		self.ml.setList(map(self._defaultlisthoster, self.streamList))
		CoverHelper(self['coverArt']).getCover(self.cover)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['liste'].getCurrent()[0][1]
		get_stream_link(self.session).check_link(url, self.playfile)

	def playfile(self, stream_url):
		if stream_url:
			self.session.open(SimplePlayer, [(self.stream_name, stream_url, self.cover)], showPlaylist=False, ltype='solarmovie', cover=True)