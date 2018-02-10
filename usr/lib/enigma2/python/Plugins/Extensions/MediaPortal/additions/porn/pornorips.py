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

BASE_NAME = "PornoRips"
default_cover = "file://%s/pornorips.png" % (config.mediaportal.iconcachepath.value + "logos")

class pornoRipsGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(BASE_NAME)
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.genreData)

	def genreData(self):
		self.genreliste.append(("--- Search ---", None))
		self.genreliste.append(("Newest (Clips)", "http://pornorips.com/category/clips/"))
		self.genreliste.append(("Newest (Movies)", "http://pornorips.com/category/movies/"))
		self.genreliste.append(("HD", "http://pornorips.com/category/hd-porn/"))
		self.genreliste.append(("Clips", None))
		self.genreliste.append(("Movies", None))
		self.genreliste.append(("Classic/Vintage", "http://pornorips.com/category/classic-porn/"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			Link = self.suchString
			Name = self['liste'].getCurrent()[0][0]
			self.session.open(pornoRipsFilmScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		if not config.mediaportal.premiumize_use.value and not config.mediaportal.realdebrid_use.value:
			message = self.session.open(MessageBoxExt, _("%s only works with enabled MP premiumize.me or Real-Debrid.com option (MP Setup)!" % BASE_NAME), MessageBoxExt.TYPE_INFO, timeout=10)
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		elif Link != None:
			self.session.open(pornoRipsFilmScreen, Link, Name)
		else:
			self.session.open(pornoRipsSubGenreScreen, Name)

class pornoRipsSubGenreScreen(MPScreen):

	def __init__(self, session, Name):
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(BASE_NAME)
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://pornorips.com/"
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		preparse = re.findall('id="catlist">.*class="catlist">', data, re.S|re.I)
		parse = re.findall('>'+self.Name+'.*'+self.Name+'\/.*?</ul>', preparse[0], re.S|re.I)
		raw = re.findall('<li\sclass="cat-item.*?a\shref="(.*?)".*?>(.*?)</a>', parse[0], re.S)
		if raw:
			self.genreliste = []
			for (Url, Title) in raw:
				Title = Title.replace(' Porn','').replace(' Movies','')
				self.genreliste.append((decodeHtml(Title), Url))
			self.genreliste.sort()
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(pornoRipsFilmScreen, Link, Name)

class pornoRipsFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label(BASE_NAME)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['name'] = Label(_("Please wait..."))
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
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "http://pornorips.com/?s=%s&limit=12&bpaged=%s" % (self.Link, str((self.page-1)*12))
		else:
			if self.page == 1:
				url = self.Link
			else:
				url = self.Link + "page/" + str(self.page) + "/"
		getPage(url).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self['name'].setText(_("Please wait..."))
		if not re.match(".*?Search", self.Name):
			self.getLastPage(data, 'class=\'wp-pagenavi\'>(.*?)</div>', '.*/page/(\d+)/')
		else:
			self.getLastPage(data, '', 'class=\'pages\'>Page.*?of\s(.*?)</span>')
		MoviesL = re.findall('class="freepostbox"(.*?)/span>', data, re.S)
		if not MoviesL:
			MoviesL = re.findall('class="post"(.*?</div.*?</div.*?</div)', data, re.S)
		if MoviesL:
			for item in MoviesL:
				Movies = re.findall('<a\shref="(.*?)".*?title=\s{0,1}"Download\s(.*?)">.*?<img\s+src="(.*?)".*?">.*?">(.*?)<', item, re.S)
				if Movies:
					Tag = re.search('class="displaycat">(.*?)</div>', item, re.S)
					for (Url, Title, Image, Date) in Movies:
						Category = ''
						if Tag:
							Category = "\nCategory: " + Tag.group(1).strip().strip(",")
						Handlung = "Added: %s%s" % (Date, Category)
						if re.match('.*?siterip',Title, re.I) or re.match('.*?site rip',Title, re.I) or re.match('.*?megapack',Title, re.I):
							pass
						else:
							self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
				else:
					Movies = re.findall('<a\shref="(.*?)".*?title=".*?">(.*?)</a>.*?displaytimesearch">.*?">(.*?)</div>.*?<img\s+src="(.*?)"', item, re.S)
					if Movies:
						for (Url, Title, Date, Image) in Movies:
							Handlung = "Added: %s" % Date
							if re.match('.*?siterip',Title, re.I) or re.match('.*?site rip',Title, re.I) or re.match('.*?megapack',Title, re.I):
								pass
							else:
								self.filmliste.append((decodeHtml(Title), Url, Image, Handlung))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), '', None, ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		handlung = self['liste'].getCurrent()[0][3]
		self['name'].setText(Title)
		self['handlung'].setText(decodeHtml(handlung))
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Title = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(pornoRipsStreamListeScreen, Link, Title)

class pornoRipsStreamListeScreen(MPScreen):

	def __init__(self, session, streamFilmLink, streamName):
		self.streamFilmLink = streamFilmLink
		self.streamName = streamName
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label(BASE_NAME)
		self['ContentTitle'] = Label("Streams:")
		self['name'] = Label(_("Please wait..."))
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.page = 1
		self.lastpage = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		url = self.streamFilmLink + "/%s/" % str(self.page)
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.getLastPage(data, 'class="link-pages">(.*?)</div>', '.*>\s{0,1}(\d+)<')
		parse = re.search('class="videosection">(.*?)class="post-calendar2', data, re.S)
		streams = re.findall('onclick="window.open.*?href="(http[s]?://(?!www.pixhost.org)(?!k2s.cc)(.*?)\/.*?)"', parse.group(1), re.S)
		if streams:
			for (stream, hostername) in streams:
				if isSupportedHoster(stream, True):
					hostername = hostername.replace('www.','')
					self.filmliste.append((hostername, stream))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No supported streams found!'), None))
		self.filmliste = list(set(self.filmliste))
		self.filmliste.sort()
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self.keyLocked = False
		self['name'].setText(self.streamName)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.streamName, stream_url)], showPlaylist=False, ltype='pornorips')