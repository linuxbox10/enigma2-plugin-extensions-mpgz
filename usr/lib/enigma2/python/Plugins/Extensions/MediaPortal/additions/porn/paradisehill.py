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
default_cover = "file://%s/paradisehill.png" % (config.mediaportal.iconcachepath.value + "logos")

class paradisehillGenreScreen(MPScreen):

	def __init__(self, session):

		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self.language = "de"
		self.suchString = ''
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://en.paradisehill.cc/porn"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<h2>Categories</h2>(.*?)<script type="', data, re.S)
		Cat = re.findall('\shref="(.*?)"\stitle="(.*?)".*?Films:(.*?)<', parse.group(1), re.S)
		if Cat:
			for (Url, Title, Count) in Cat:
				Url = Url + "?page="
				self.genreliste.append((Title, Url, Count))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Popular (All Time)", "/popular/?page=", None))
			self.genreliste.insert(0, ("Popular (Monthly)", "/popular/?filter=month&page=", None))
			self.genreliste.insert(0, ("Popular (Weekly)", "/popular/?filter=week&page=", None))
			self.genreliste.insert(0, ("Popular (Daily)", "/popular/?filter=day&page=", None))
			self.genreliste.insert(0, ("Newest", "/porn/?page=", None))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			paradisehillUrl = '%s' % (self.suchString)
			paradisehillGenre = "--- Search ---"
			count = None
			self.session.open(paradisehillFilmListeScreen, paradisehillUrl, paradisehillGenre, count)

	def keyOK(self):
		if self.keyLocked:
			return
		paradisehillGenre = self['liste'].getCurrent()[0][0]
		paradisehillUrl = self['liste'].getCurrent()[0][1]
		count = self['liste'].getCurrent()[0][2]
		if paradisehillGenre == "--- Search ---":
			self.suchen()
		else:
			self.session.open(paradisehillFilmListeScreen, paradisehillUrl, paradisehillGenre, count)

class paradisehillFilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName, count):
		self.genreLink = genreLink
		self.genreName = genreName
		self.count = count
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Genre: %s" % self.genreName)
		self['name'] = Label("Film Auswahl")
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		if re.match(".*?Search", self.genreName):
			if self.page == 1:
				url = "http://en.paradisehill.cc/search_results/?search=%s" % self.genreLink
			else:
				url = "http://en.paradisehill.cc/search_results/?search=%s&page=%s" % (self.genreLink,str(self.page))
		else:
			url = "http://en.paradisehill.cc%s%s" % (self.genreLink,str(self.page))
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if self.count and self.count != 'None':
			self.lastpage = int(round((float(self.count) / 24) + 0.5))
			self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		else:
			self.getLastPage(data, 'class="pagination(.*?)</div>' , '.*page=(\d+)">')
		parse = re.search('class="row new-collect(.*?)class="pagination', data, re.S)
		if parse:
			movies = re.findall('bci(-title|)-link" href="(.*?)".*?bci-title">(.*?)<.*?img["]? src="(.*?)"', parse.group(1), re.S)
			if movies:
				self.filmliste = []
				for (x,url,title,image) in movies:
					image = "http://en.paradisehill.cc%s" % image
					self.filmliste.append((decodeHtml(title),url,image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste,0,1,2,None,None,self.page,self.lastpage)
		self.showInfos()

	def showInfos(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		streamPic = self['liste'].getCurrent()[0][2]
		self['name'].setText(streamTitle)
		CoverHelper(self['coverArt']).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		url = "http://en.paradisehill.cc%s" % url
		self.session.open(paradisehillFilmAuswahlScreen, title, url, image)

class paradisehillFilmAuswahlScreen(MPScreen):

	def __init__(self, session, genreName, genreLink, cover):
		self.genreLink = genreLink
		self.genreName = genreName
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("ParadiseHill")
		self['ContentTitle'] = Label("Streams")
		self['name'] = Label(self.genreName)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		getPage(self.genreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('films=(.*?)\];', data, re.S)
		if parse:
			streams = re.findall('sources.*?src":"(.*?)"', parse.group(1), re.S)
		if len(streams) > 1:
			for i in range(0,len(streams),1):
				videoname = self.genreName + ' (Part ' + str(i+1) + ')'
				self.filmliste.append((videoname, streams[i].replace('\/','/')))
		elif len(streams) == 1:
			videoname = self.genreName
			self.filmliste.append((videoname, streams[0].replace('\/','/')))
		else:
			self.filmliste.append(("No streams found!",None))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink == None:
			return
		url = streamLink
		url = url.replace('&amp;','&').replace('&#038;','&')
		title = self.genreName
		mp_globals.player_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3'
		self.session.open(SimplePlayer, [(title, url, self.cover)], showPlaylist=False, ltype='paradisehill', cover=True)