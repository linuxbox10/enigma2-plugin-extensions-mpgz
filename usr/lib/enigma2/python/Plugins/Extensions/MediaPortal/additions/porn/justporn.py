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
default_cover = "file://%s/justporn.png" % (config.mediaportal.iconcachepath.value + "logos")

class justPornGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("JustPorn")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.filmliste = []
		url = "http://justporn.to/"
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		parse = re.search('Genre</a>(.*?)>Herkunft</a>', data, re.S)
		raw = re.findall('class="cat-item\scat-item-.*?"><a\shref="(.*?)"\s>(.*?)</a>', parse.group(1), re.S)
		if raw:
			for (Url, Title) in raw:
				Url = Url + "page/"
				self.filmliste.append((decodeHtml(Title), Url))
			self.filmliste.sort()
			self.filmliste.insert(0, ("Neue Scenes", "http://justporn.to/category/scenes/page/", None))
			self.filmliste.insert(0, ("Neue DVDRips", "http://justporn.to/category/dvdrips-full-movies/page/", None))
			self.filmliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.ml.setList(map(self._defaultlistcenter, self.filmliste))
			self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '-')
			Link = self.suchString
			Name = self['liste'].getCurrent()[0][0]
			self.session.open(justPornListScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(justPornListScreen, Link, Name)

class justPornListScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
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

		self['title'] = Label("JustPorn")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))

		self.keyLocked = True
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.page = 1
		self.lastpage = 1
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "http://justporn.to/page/" + str(self.page) + "/?s=" + self.Link
		else:
			url = self.Link + str(self.page)
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, '', "class='pages'>.*?von\s(.*?)<")
		raw = re.findall('<h2><a\shref="(.*?)".*?title="(.*?)">.*?src="(.*?)".*?duration">(.*?)</span>', data, re.S)
		if raw:
			for (link, title, image, duration) in raw:
				self.filmliste.append((decodeHtml(title), link, image, duration))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.ml.moveToIndex(0)
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, ""))
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		runtime = self['liste'].getCurrent()[0][3]
		self['handlung'].setText("Runtime: %s" % (runtime))
		self['name'].setText(title)
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][0]
		if Link:
			Title = self['liste'].getCurrent()[0][1]
			Cover = self['liste'].getCurrent()[0][2]
			self.session.open(StreamAuswahl, Link, Title, Cover)

class StreamAuswahl(MPScreen):

	def __init__(self, session, Title, Link, Cover):
		self.Link = Link
		self.Title = Title
		self.Cover = Cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("JustPorn")
		self['ContentTitle'] = Label("%s" %self.Title)

		self.filmliste = []
		self.keyLocked = True
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		CoverHelper(self['coverArt']).getCover(self.Cover)
		self.keyLocked = True
		url = self.Link
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		streams = re.findall('(?:src=|href=|)[out\/\?|\'|"](http[s]?://(?!(justporn.to|pichost.biz))(.*?)\/.*?)[\'|"|\&|<]', data, re.S|re.I)
		if streams:
			for (stream, dummy, hostername) in streams:
				if isSupportedHoster(hostername, True):
					hostername = hostername.replace('www.','').replace('embed.','').replace('play.','')
					self.filmliste.append((hostername, stream))
			# remove duplicates
			self.filmliste = list(set(self.filmliste))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No supported streams found!'), None))
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		title = self.Title
		self.session.open(SimplePlayer, [(self.Title, stream_url, self.Cover)], showPlaylist=False, ltype='justporn', cover=True)