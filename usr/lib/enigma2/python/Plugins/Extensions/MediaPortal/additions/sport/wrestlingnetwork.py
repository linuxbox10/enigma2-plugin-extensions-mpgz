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

class wrestlingnetworkGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		if self.mode == "watchwrestling":
			self.portal = "Watch Wrestling In"
			self.baseurl = "http://watchwrestling.in"
		if self.mode == "watchwrestlinguno":
			self.portal = "Watch Wrestling Uno"
			self.baseurl = "http://watchwrestling.uno"

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre:")
		self['name'] = Label(_("Please wait..."))

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = []
		url = self.baseurl
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('id="main-nav">(.*?)</div>', data, re.S)
		if raw:
			parse = re.findall('<li.*?href="(.*?)">(.*?)</a>', raw[0], re.S)
			for (url, title) in parse:
				self.genreliste.append((decodeHtml(title), url))
			# remove duplicates
			self.genreliste = list(set(self.genreliste))
			#self.genreliste.sort()
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False
			self.showInfos()
		self['name'].setText('')

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Url = self['liste'].getCurrent()[0][1]
		self.session.open(wrestlingnetworkListeScreen, Name, Url, self.portal)

class wrestlingnetworkListeScreen(MPScreen):

	def __init__(self, session, Name,Link, portal):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self.keyLocked = True
		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Genre: %s" % self.Name)

		self['Page'] = Label(_("Page:"))
		self.page = 1
		self.lastpage = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		url = "%spage/%s" % (self.Link ,str(self.page))
		getPage(url).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if re.search('<link rel="next"', data):
			self.lastpage = self.page + 1
			self['page'].setText(str(self.page) + ' + ')
		else:
			self['page'].setText(str(self.page))
		raw = re.findall('id="main">(.*?)id="sidebar"', data, re.S)
		shows = re.findall('clip-link.*?title="(.*?)" href="(.*?)".*?src="(.*?)"', raw[0], re.S)
		if shows:
			self.filmliste = []
			for (title,url,image) in shows:
				self.filmliste.append((decodeHtml(title),url,image))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Url = self['liste'].getCurrent()[0][1]
		self.session.open(wrestlingnetworkPlayer, Name, Url, self.portal)

class wrestlingnetworkPlayer(MPScreen):

	def __init__(self, session, Name, Url, portal):
		self.Name = Name
		self.Url = Url
		self.portal = portal
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label(self.portal)
		self['ContentTitle'] = Label("Videos: %s" %self.Name)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.getVideo)

	def getVideo(self):
		getPage(self.Url).addCallback(self.getData).addErrback(self.dataError)

	def getData(self, data):
		if re.match('.*?Link will added in Few Hours', data, re.S):
			self.filmliste.append((_("Link will added in few Hours!"), None, False))
			self.keyLocked = True
		else:
			vid = re.findall('href="(http[s]?://[^<>]*?)"\sclass="su-button.*?webkit-text-shadow:none">(.*?)</span>', data, re.S)
			if vid:
				for (url, title) in vid:
					self.filmliste.append((decodeHtml(title), url, False))
			else:
				streams = re.findall('(http[s]?://(.*?)\/.*?)[\'|"|\&|<]', data, re.S)
				if streams:
					for (stream, hostername) in streams:
						if isSupportedHoster(hostername, True):
							hostername = hostername.replace('www.','').replace('embed.','').replace('play.','')
							self.filmliste.append((hostername, stream, True))
		self.keyLocked = False
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		host = self['liste'].getCurrent()[0][2]
		if host:
			get_stream_link(self.session).check_link(url, self.got_link)
		if url:
			getPage(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml','Referer': self.Url}).addCallback(self.getExtraData).addErrback(self.dataError)

	def getExtraData(self, data):
		url = re.findall('<iframe.*?src="(http[s]?://www.dailymotion.com/embed/video/.*?)"', data, re.S)
		if url:
			getPage(url[0]).addCallback(self.getStream).addErrback(self.dataError)

	def getStream(self, data):
		data = data.replace("\\/", "/")
		title = self['liste'].getCurrent()[0][0]
		title = self.Name + " - " + title
		stream_url = re.findall('"(240|380|480|720)".*?url":"(http[s]?://www.dailymotion.com/cdn/.*?)"', data, re.S)
		if stream_url:
			self.session.open(SimplePlayer, [(title, stream_url[-1][1])], showPlaylist=False, ltype='wrestling', forceGST=True)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.Name, stream_url)], showPlaylist=False, ltype='wrestling')