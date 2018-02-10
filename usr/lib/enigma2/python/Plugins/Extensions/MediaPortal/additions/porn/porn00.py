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

myagent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0'
default_cover = "file://%s/porn00.png" % (config.mediaportal.iconcachepath.value + "logos")

class porn00GenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label("porn00.org")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.porn00.org/"
		twAgentGetPage(url, agent=myagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('id="categorias"(.*?)<div id="peu">', data, re.S)
		Cats = re.findall("href='(.*?)'.*?>(.*?)</a>", parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = Url + 'page/'
				self.genreliste.append((Title.title(), Url))
			self.genreliste.sort()
		self.genreliste.insert(0, ("Newest", "http://www.porn00.org/page/"))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(porn00FilmScreen, Link, Name)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(porn00FilmScreen, Link, Name)

class porn00FilmScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("porn00.org")
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
		if re.match(".*?Search", self.Name):
			url = "http://www.porn00.org/page/%s/?s=%s" % (str(self.page), self.Link)
		else:
			url = "%s%s" % (self.Link, str(self.page))
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, "id='pagination'>(.*?)</div>")
		Movies = re.findall('class="player".*?title="(.*?)".*?href="(.*?)".*?img.*?src="(.*?)".*?alt=', data, re.S)
		if Movies:
			for (Title, Url, Image) in Movies:
				if not re.match('http[s]?://', Url):
					Url = 'http://www.porn00.org'+Url
				self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		Url = self['liste'].getCurrent()[0][1]
		if Url == None:
			return
		pic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		self.session.open(porn00FilmAuswahlScreen, title, url, image)

class porn00FilmAuswahlScreen(MPScreen):

	def __init__(self, session, genreName, genreLink, cover):
		self.genreLink = genreLink
		self.genreName = genreName
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.altcounter = 1
		self.keyLocked = True
		self['title'] = Label("porn00.org")
		self['ContentTitle'] = Label("Streams")
		self['name'] = Label(self.genreName)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		twAgentGetPage(self.genreLink, agent=myagent).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		preparse = re.search('<div id="central">(.*?)<div class="video gran">', data, re.S)
		if preparse:
			alternativ = re.findall('>Alternative \w.*? <a href="(.*?)"', preparse.group(1), re.S)
			if alternativ:
				self.altcounter += len(alternativ)
				for link in alternativ:
					self.getAlternativLink(link)
		self.getVideoLink(data)

	def getAlternativLink(self, url):
		twAgentGetPage(url, agent=myagent).addCallback(self.getVideoLink).addErrback(self.dataError)

	def getVideoLink(self,data):
		self.altcounter -= 1
		parse = re.search('<div class="imatge alta">(.*?)type="text/javascript">', data, re.S)
		streams = re.findall('src="((http:|https:|)//(.*?)/.*?)"', parse.group(1), re.S)
		if streams:
			for (stream, urlstart, hostername) in streams:
				if not re.search('.*?\?v=22$',stream):
					if 'http://porn00.org/video_ext.php' in stream:
						hostername = 'porn00 vk'
					elif 'http://www.porn00.org/video_ext.php' in stream:
						hostername = 'porn00 pornaq'
					elif 'http://www.porn00.org/play/?v=' in stream:
						hostername = 'porn00 direct'
					elif hostername == 'www.wankz.com':
						hostername = 'porn00 wankz'
					elif re.search('http://www.porn00.org/(player|video|server|watch|plays)/\?.=.*?', stream):
						hostername = 'porn00 direct'
					if re.match('porn00 ', hostername) or isSupportedHoster(hostername, True):
						self.filmliste.append((hostername, stream))
		if self.altcounter == 0:
			if len(self.filmliste) == 0:
				self.filmliste.append(("No supported streams found!",None))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False
		CoverHelper(self['coverArt']).getCover(self.cover)

	def keyOK(self):
		if self.keyLocked:
			return
		hoster = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		if url == None:
			return
		url = url.replace('&amp;','&').replace('&#038;','&')
		if hoster == 'porn00 vk':
			url = url.replace('porn00.org', 'vk.com')
			get_stream_link(self.session).check_link(url, self.got_link)
		elif hoster == 'porn00 pornaq':
			twAgentGetPage(url, agent=myagent).addCallback(self.porn00pornaqData).addErrback(self.dataError)
		elif hoster == 'porn00 direct':
			twAgentGetPage(url, agent=myagent).addCallback(self.porn00directData).addErrback(self.dataError)
		elif hoster == 'porn00 wankz':
			twAgentGetPage(url, agent=myagent).addCallback(self.porn00wankzData).addErrback(self.dataError)
		else:
			get_stream_link(self.session).check_link(url, self.got_link)

	def porn00wankzData(self, data):
		stream_url = re.findall('name:"\d+p",url:"(.*?)"', data)
		if stream_url:
			self.got_link(stream_url[0])
		else:
			message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def porn00pornaqData(self, data):
		link = re.findall('src\',\s*\'(http.*?)\'', data)
		if link:
			cryptlink = urllib.unquote(link[-1].replace('\\x','%'))
			get_stream_link(self.session).check_link(cryptlink, self.got_link)
		else:
			message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def porn00directData(self,data):
		link = re.findall('file:\s*["|\'](http.*?)["|\']', data)
		if link:
			self.got_link(link[-1])
			return
		else:
			link = re.findall('var\szu\s=\s["|\'](http.*?)["|\']', data)
			if not link:
				link = re.findall('var\sro\s=\s["|\'](http.*?)["|\']', data)
			if link:
				self.got_link(link[-1])
				return
		message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def got_link(self, stream_url):
		title = self.genreName
		self.session.open(SimplePlayer, [(title, stream_url, self.cover)], showPlaylist=False, ltype='porn00', cover=True)