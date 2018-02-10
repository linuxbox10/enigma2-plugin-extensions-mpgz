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

javagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

class javhd3xGenreScreen(MPScreen):

	def __init__(self, session, mode):
		self.mode = mode

		if self.mode == "javhd3x":
			self.portal = "JAVHD3X"
			self.baseurl = "javhd3x.com"
			self.delim = "+"
			self.default_cover = "file://%s/javhd3x.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javhd4k":
			self.portal = "JAVHD4K"
			self.baseurl = "javhd4k.com"
			self.delim = "+"
			self.default_cover = "file://%s/javhd4k.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornhd3x":
			self.portal = "PORNHD3X"
			self.baseurl = "pornhd3x.to"
			self.delim = "+"
			self.default_cover = "file://%s/pornhd3x.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "javfun":
			self.portal = "JAVFUN.NET"
			self.baseurl = "javfun.net"
			self.delim = "%20"
			self.default_cover = "file://%s/javfun.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "jav555":
			self.portal = "JAV555.NET"
			self.baseurl = "jav555.net"
			self.delim = "%20"
			self.default_cover = "file://%s/jav555.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornhdx":
			self.portal = "PORNHDX.TO"
			self.baseurl = "pornhdx.to"
			self.delim = "%20"
			self.default_cover = "file://%s/pornhdxto.png" % (config.mediaportal.iconcachepath.value + "logos")
		elif self.mode == "pornhd8k":
			self.portal = "PORNHD8K.NET"
			self.baseurl = "pornhd8k.net"
			self.delim = "%20"
			self.default_cover = "file://%s/pornhd8k.png" % (config.mediaportal.iconcachepath.value + "logos")

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

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
		CoverHelper(self['coverArt']).getCover(self.default_cover)
		self.keyLocked = True
		url = "http://%s/" % self.baseurl
		twAgentGetPage(url, agent=javagent).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		Cats = re.findall('href=[\'|\"](\/(?:category|studio)\/.*?)[\'|\"].*?>(.*?)</a', data, re.S)
		if Cats:
			dup_items = set()
			for (Url, Title) in Cats:
				if not Url.startswith('http'):
					Url = 'http://' + self.baseurl + Url
				if Url.lower() not in dup_items:
					self.genreliste.append((Title, Url.lower()))
					dup_items.add(Url.lower())
			self.genreliste = list(set(self.genreliste))
			self.genreliste.sort(key=lambda t : t[0].lower())

		if self.mode == "pornhd3x":
			maincat = "porn-movies"
		elif self.mode == "pornhdx":
			maincat = "porn-hd-videos"
		elif self.mode == "pornhd8k":
			maincat = "porn-hd-videos"
		else:
			maincat = "japanese-porn-videos"
		if self.mode == "jav555" or self.mode == "javfun":
			self.genreliste.insert(0, ("More Genres", "https://%s/category" % self.baseurl, None))
		if self.mode == "pornhd3x":
			self.genreliste.insert(0, ("Pornstars", "https://%s/pornstars" % self.baseurl, None))
		self.genreliste.insert(0, ("Newest", "http://%s/%s" % (self.baseurl, maincat), None))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen", None))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', self.delim)
			Name = "--- Search ---"
			Link = '%s' % (self.suchString)
			self.session.open(javhd3xFilmScreen, Link, Name, self.portal, self.baseurl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		if Name == "--- Search ---":
			self.suchen()
		else:
			Link = self['liste'].getCurrent()[0][1]
			self.session.open(javhd3xFilmScreen, Link, Name, self.portal, self.baseurl)

class javhd3xFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name, portal, baseurl):
		self.Link = Link
		self.Name = Name
		self.portal = portal
		self.baseurl = baseurl
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
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
			if self.portal == "JAVHD3X":
				url = "http://%s/tim-kiem?key=%s&page=%s" % (self.baseurl, self.Link, str(self.page))
			elif self.portal == "JAVHD4K" or self.portal == "PORNHD3X":
				url = "http://%s/search?key=%s&page=%s" % (self.baseurl, self.Link, str(self.page))
			else:
				if self.page > 1:
					url = "http://%s/search/%s/page-%s" % (self.baseurl, self.Link, str(self.page))
				else:
					url = "http://%s/search/%s" % (self.baseurl, self.Link)
		else:
			if self.page > 1:
				url = self.Link + "/page-" + str(self.page)
			else:
				url = self.Link
		twAgentGetPage(url, agent=javagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, '"pagination">(.*?)</div>', '.*(?:\/|\&)page(?:\-|\=)(\d+)')
		Movies = re.findall('class="(?:video|ml)-item">.*?href=[\'|\"](.*?)[\'|\"].*?title="(.*?)".*?img\s(?:src|data-original)="(.*?)"', data, re.S)
		if Movies:
			for (Url, Title, Image) in Movies:
				if not Image and "/category/" in Url:
					pass
				else:
					if not Image.startswith('http'):
						Image = 'http://' + self.baseurl + Image
					if not Url.startswith('http'):
						Url = 'http://' + self.baseurl + Url
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
		pic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(pic)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			if "/category/" in url or "/profile/" in url:
				Name = self['liste'].getCurrent()[0][0]
				Link = url
				self.session.open(javhd3xFilmScreen, Link, Name, self.portal, self.baseurl)
			else:
				twAgentGetPage(url, agent=javagent).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		uuid = re.findall('<input.*?id="uuid".*?value="(.*?)"', data, re.S)
		if uuid:
			ajax = re.findall('ajax\({url:\s\"(.*?)\"\s', data, re.S)
			if ajax:
				url = 'http://%s/%s/%s' % (self.baseurl, ajax[0].strip('/'), uuid[0])
			else:
				ajax = re.findall('ajax\({url:\s(.*?)\s', data, re.S)
				uri = re.findall('var\s_0x[a-fA-F0-9]+=\[\"(.*?)\"\];.*?var\s%s' % ajax[0], data, re.S)
				if not uri:
					ajax2 = re.findall('var\s%s=(.*?)\[\d\]' % ajax[0], data, re.S)
					uri = re.findall('var\s%s=\[\"(.*?)\"\]' % ajax2[0], data, re.S)
				url = 'http://%s/%s/%s' % (self.baseurl, uri[0].decode('string_escape').strip('/'), uuid[0])
			twAgentGetPage(url, agent=javagent).addCallback(self.getVideoLink).addErrback(self.dataError)

	def getVideoLink(self, data):
		videos = re.findall('file":\sDec\("(.*?)"\).*?label":"(\d+)', data, re.S|re.I)
		parse = re.search('.*?(?:type="hidden" id="uuid"|invideo)(.*?)GibberishAES', data, re.S)
		if parse:
			deckey = re.findall('var\s_0x[0-9a-f]+=\[\"(.*?)\"', parse.group(1), re.S)
			cryptkey = deckey[-1].decode('string_escape')
			from Plugins.Extensions.MediaPortal.resources.porncrypt import decrypt
			videoLink = decrypt(videos[-1][0], key=cryptkey)
			title = self['liste'].getCurrent()[0][0]
			mp_globals.player_agent = javagent
			if "googleusercontent.com" in videoLink:
				get_stream_link(self.session).check_link(videoLink, self.got_link)
			else:
				self.session.open(SimplePlayer, [(title, videoLink)], showPlaylist=False, ltype='javhd3x')

	def got_link(self, stream_url):
		title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(title, stream_url)], showPlaylist=False, ltype='javhd3x')