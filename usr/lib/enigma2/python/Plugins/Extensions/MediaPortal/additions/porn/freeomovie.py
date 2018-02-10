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
default_cover = "file://%s/freeomovie.png" % (config.mediaportal.iconcachepath.value + "logos")

class freeomovieGenreScreen(MPScreen):

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
		self['title'] = Label("freeomovie.com")
		self['ContentTitle'] = Label("Genres")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.freeomovie.com/"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('Categories</h3>(.*?)</div>', data, re.S)
		Cat = re.findall('href="(.*?)".*?>(.*?)</a></li>', parse.group(1), re.S)
		if Cat:
			for (Url, Title) in Cat:
				Url = Url + "page/"
				if Title not in ["XXX Comics", "XXX Games"]:
					self.genreliste.append((Title, Url))
			self.genreliste.sort()
			self.genreliste.insert(0, ("Newest", "http://www.freeomovie.com/page/"))
			self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			freeomovieUrl = '%s' % (self.suchString)
			freeomovieGenre = "--- Search ---"
			self.session.open(freeomovieFilmListeScreen, freeomovieUrl, freeomovieGenre)

	def keyOK(self):
		if self.keyLocked:
			return
		freeomovieGenre = self['liste'].getCurrent()[0][0]
		freeomovieUrl = self['liste'].getCurrent()[0][1]
		if freeomovieGenre == "--- Search ---":
			self.suchen()
		else:
			self.session.open(freeomovieFilmListeScreen, freeomovieUrl, freeomovieGenre)

class freeomovieFilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName):
		self.genreLink = genreLink
		self.genreName = genreName
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
		self['title'] = Label("freeomovie.com")
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
			url = "http://www.freeomovie.com/page/%s/?s=%s" % (str(self.page),self.genreLink)
		else:
			url = "%s%s" % (self.genreLink,str(self.page))
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.getLastPage(data, 'class=[\"|\']wp-pagenavi[\"|\']>(.*?)</div>')
		movies = re.findall('class="boxtitle">.*?<a href="(.*?)".*?title="(.*?)".*?<img src="(.*?)"', data, re.S)
		if movies:
			self.filmliste = []
			for (url,title,image) in movies:
				self.filmliste.append((decodeHtml(title),url,image))
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
		getPage(streamUrl).addCallback(self.getDescription).addErrback(self.dataError)

	def getDescription(self, data):
		ddDescription = re.search('name="description"\scontent="(.*?)"', data, re.S)
		if ddDescription:
			self['handlung'].setText(decodeHtml(ddDescription.group(1)))
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		if self.keyLocked:
			return
		title = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		image = self['liste'].getCurrent()[0][2]
		self.session.open(freeomovieFilmAuswahlScreen, title, url, image)

class freeomovieFilmAuswahlScreen(MPScreen):

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
		self['title'] = Label("freeomovie.com")
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
		parse = re.search('class="videosection">(.*?)class="textsection">', data, re.S)
		streams = re.findall('(http[s]?://(.*?)\/.*?)[\'|"|\&|<]', parse.group(1) , re.S)
		if streams:
			for (stream, hostername) in streams:
				if isSupportedHoster(hostername, True):
					disc = re.search('.*?(CD-1|CD1|CD-2|CD2|_a.avi|_b.avi|-a.avi|-b.avi|DISC1|DISC2).*?', stream, re.S|re.I)
					if disc:
						discno = disc.group(1)
						discno = discno.replace('cd1','Teil 1').replace('cd2','Teil 2').replace('CD1','Teil 1').replace('CD2','Teil 2').replace('CD-1','Teil 1').replace('CD-2','Teil 2').replace('_a.avi','Teil 1').replace('_b.avi','Teil 2')
						discno = discno.replace('-a.avi','Teil 1').replace('-b.avi','Teil 2').replace('DISC1','Teil 1').replace('DISC2','Teil 2').replace('Disc1','Teil 1').replace('Disc2','Teil 2')
						hostername = hostername + ' (' + discno + ')'
					self.filmliste.append((hostername, stream))
			# remove duplicates
			self.filmliste = list(set(self.filmliste))
		if len(self.filmliste) == 0:
			self.filmliste.append(("No supported streams found!", None))
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			url = url.replace('&amp;','&').replace('&#038;','&')
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		title = self.genreName
		self.session.open(SimplePlayer, [(title, stream_url, self.cover)], showPlaylist=False, ltype='freeomovie', cover=True)