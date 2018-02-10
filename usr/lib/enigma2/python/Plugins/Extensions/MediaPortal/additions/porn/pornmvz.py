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

class pornmvzGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self.language = "de"
		self.suchString = ''
		self['title'] = Label("PORNMVZ.com")
		self['ContentTitle'] = Label("Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://pornmvz.com/"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('>Categories<(.*?)</div>', data, re.S)
		if parse:
			Cat = re.findall('<a href="(.*?)">(.*?)<', parse.group(1), re.S)
			if Cat:
				for (Url, Title) in Cat:
					Url = '%s&paged=' % Url
					self.genreliste.append((Title, Url))
				self.genreliste.sort()
				self.genreliste.insert(0, ("Newest", "http://pornmvz.com/?paged="))
				self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
				self.ml.setList(map(self._defaultlistcenter, self.genreliste))
				self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			pornmvzUrl = '%s' % (self.suchString)
			pornmvzGenre = "--- Search ---"
			self.session.open(pornmvzFilmListeScreen, pornmvzUrl, pornmvzGenre)

	def keyOK(self):
		if self.keyLocked:
			return
		pornmvzGenre = self['liste'].getCurrent()[0][0]
		pornmvzUrl = self['liste'].getCurrent()[0][1]
		if pornmvzGenre == "--- Search ---":
			self.suchen()
		else:
			self.session.open(pornmvzFilmListeScreen, pornmvzUrl, pornmvzGenre)

class pornmvzFilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName):
		self.genreLink = genreLink
		self.genreName = genreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
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
		self['title'] = Label("PORNMVZ.com")
		self['ContentTitle'] = Label("%s" % self.genreName)
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
			url = "http://pornmvz.com/?s=%s&paged=%s" % (self.genreLink,str(self.page))
		else:
			url = "%s%s" % (self.genreLink,str(self.page))
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.filmliste = []
		self.getLastPage(data, 'id="post-navigator">(.*?)</div>', '.*paged=(\d+)"')
		parts = re.findall('<div class="respl-item.*?<a href="(http://pornmvz.com/.*?src=".*?)"', data, re.S)
		if parts:
			for part in parts:
				movie = re.findall('^(http://pornmvz.com/.*?)"\s{0,2}title=".*?([a-zA-Z0-9].*?)"\s>.*?src="(.*?)$', part, re.S)
				if movie:
					for (url,title,image) in movie:
						self.filmliste.append((decodeHtml(title),url,image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage)
		self.showInfos()

	def showInfos(self):
		streamTitle = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		streamPic = self['liste'].getCurrent()[0][2]
		self['name'].setText(streamTitle)
		CoverHelper(self['coverArt']).getCover(streamPic)
		getPage(streamUrl).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.search('class="post-content-single">\n<center>.*?</a><br\s/>\n{0,1}(.*?)<br\s/>.*?</center>', data, re.S)
		if ddDescription:
			if ddDescription.group(1) == "&#8230;":
				self['handlung'].setText(_("No further information available!"))
			else:
				self['handlung'].setText(decodeHtml(ddDescription.group(1)))
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		self.session.open(pornmvzFilmAuswahlScreen, title, url, image)

class pornmvzFilmAuswahlScreen(MPScreen):

	def __init__(self, session, genreName, genreLink, cover):
		self.genreLink = genreLink
		self.genreName = genreName
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("PORNMVZ.com")
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
		parse = re.search('class="itemFullText">(.*?)id="content_right"', data, re.S)
		if parse:
			streams = re.findall('(http://(.*?)\/.*?)[\'|"|\&|<]', parse.group(1) , re.S)
			if streams:
				for (stream, hostername) in streams:
					if isSupportedHoster(hostername, True):
						hostername = hostername.replace('www.','').replace('embed.','').replace('play.','')
						self.filmliste.append((hostername, stream))
				# remove duplicates, keep order
				self.filmliste = reduce(lambda x, y: x if y in x else x + [y], self.filmliste, [])
		if len(self.filmliste) == 0:
			self.filmliste.append(("No supported streams found!",None))
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self.keyLocked = False
		CoverHelper(self['coverArt']).getCover(self.cover)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			url = url.replace('&amp;','&').replace('&#038;','&')
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		title = self.genreName
		self.session.open(SimplePlayer, [(title, stream_url, self.cover)], showPlaylist=False, ltype='pornmvz', cover=True)