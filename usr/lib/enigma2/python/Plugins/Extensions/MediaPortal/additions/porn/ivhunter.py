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

ivhagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

default_cover = "file://%s/ivhunter.png" % (config.mediaportal.iconcachepath.value + "logos")

class ivhunterGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		if self.mode == "ivhunter":
			self.portal = "IVHUNTER"
			self.baseurl = "ivhunter.com"
			self.delim = "+"

		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel
		}, -1)

		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://%s/" % self.baseurl
		twAgentGetPage(url, agent=ivhagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('href=[\'|\"].*?(\/studios\/.*?)[\'|\"].*?>(.*?)</a', data, re.S)
		if Cats:
			dup_items = set()
			for (Url, Title) in Cats:
				if not Url.startswith('http'):
					Url = 'http://' + self.baseurl + Url
				if Url.lower() not in dup_items:
					if Title != "Studios":
						self.genreliste.append((Title, Url.lower(), None))
						dup_items.add(Url.lower())
			self.genreliste = list(set(self.genreliste))
			self.genreliste.append(("Junior Idol", "http://%s/junior-idol/" % self.baseurl, None))
			self.genreliste.sort(key=lambda t : t[0].lower())
		self.genreliste.insert(0, ("HD", "http://%s/hd-video/" % self.baseurl, None))
		self.genreliste.insert(0, ("Newest", "http://%s/" % self.baseurl, None))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', self.delim)
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(ivhunterFilmScreen, Link, Name, self.portal, self.baseurl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(ivhunterFilmScreen, Link, Name, self.portal, self.baseurl)

class ivhunterFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"upUp" : self.key_repeatedUp,
			"rightUp" : self.key_repeatedUp,
			"leftUp" : self.key_repeatedUp,
			"downUp" : self.key_repeatedUp,
			"upRepeated" : self.keyUpRepeated,
			"downRepeated" : self.keyDownRepeated,
			"rightRepeated" : self.keyRightRepeated,
			"leftRepeated" : self.keyLeftRepeated,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label(self.portal)
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
			if self.page > 1:
				url = "http://%s/page/%s/?s=%s" % (self.baseurl, str(self.page), self.Link)
			else:
				url = "http://%s/?s=%s" % (self.baseurl, self.Link)
		else:
			if self.page > 1:
				url = self.Link + "page/" + str(self.page)
			else:
				url = self.Link
		twAgentGetPage(url, agent=ivhagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class=\'wp-pagenavi\'>(.*?)</div>', '.*\/page\/(\d+)')
		Movies = re.findall('id="post-\d+".*?clip-link.*?title="(.*?)"\shref="(.*?)".*?img\ssrc="(.*?)"', data, re.S)
		if Movies:
			for (Title, Url, Image) in Movies:
				if not Image and "/category/" in Url:
					pass
				else:
					if not Image.startswith('http'):
						Image = 'http://' + self.baseurl + Image
					Image = Image.replace('https://pics.dmm.co.jp','http://pics.dmm.co.jp').replace('https://pics.dmm.com','http://pics.dmm.co.jp')
					if not Url.startswith('http'):
						Url = 'http://' + self.baseurl + Url
					self.filmliste.append((decodeHtml(Title), Url, Image))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.loadPicQueued()

	def showInfos(self):
		CoverHelper(self['coverArt']).getCover(default_cover)
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)

	def loadPic(self):
		if self.picQ.empty():
			self.eventP.clear()
			return
		while not self.picQ.empty():
			self.picQ.get_nowait()
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]
		self.showInfos()
		self.updateP = 1
		CoverHelper(self['coverArt'], self.ShowCoverFileExit).getCover(streamPic)

	def keyOK(self):
		if self.keyLocked:
			return
		self['name'].setText(_('Please wait...'))
		self.keyLocked = True
		url = self['liste'].getCurrent()[0][1]
		if url:
			twAgentGetPage(url, agent=ivhagent).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		streams = re.findall('<iframe src="(https://openload.co/embed/[a-zA-Z0-9]+\/)"', data, re.S)
		if streams:
			get_stream_link(self.session).check_link(streams[0], self.got_link)
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)
			self.keyLocked = False

	def got_link(self, stream_url):
		self.keyLocked = False
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		mp_globals.player_agent = ivhagent
		self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='ivhunter')