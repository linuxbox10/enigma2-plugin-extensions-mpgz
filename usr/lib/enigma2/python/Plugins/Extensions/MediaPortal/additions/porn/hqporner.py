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
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper
from Plugins.Extensions.MediaPortal.resources.packer import unpack, detect
default_cover = "file://%s/hqporner.png" % (config.mediaportal.iconcachepath.value + "logos")
hqAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36"

class hqpornerGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("HQPORNER")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.genreData)

	def genreData(self):
		self.filmliste.append(("--- Search ---", None))
		self.filmliste.append(("Newest", "http://hqporner.com/hdporn"))
		self.filmliste.append(("Genres", "categories"))
		self.filmliste.append(("Studios", "studios"))
		self.filmliste.append(("Girls", "girls"))
		self.ml.setList(map(self._defaultlistcenter, self.filmliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			Link = self.suchString
			Name = self['liste'].getCurrent()[0][0]
			self.session.open(hqpornerListScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		elif re.search('http://.*?', Link):
			self.session.open(hqpornerListScreen, Link, Name)
		else:
			self.session.open(hqpornerSubGenreScreen, Link, Name)

class hqpornerSubGenreScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("HQPORNER")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = "http://hqporner.com/" + self.Link
		getPage(url, agent=hqAgent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw = re.findall('class="box\sfeature">\s+<a href="(.*?)".*?img\ssrc="(.*?)"[\s]?alt="(.*?)"', data, re.S)
		if raw:
			for (Url, Image, Title) in raw:
				Url = "http://hqporner.com" + Url
				Image = "http://hqporner.com/" + Image
				self.filmliste.append((decodeHtml(Title.title()), Url, Image))
			self.filmliste.sort()
			self.ml.setList(map(self._defaultlistcenter, self.filmliste))
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(hqpornerListScreen, Link, Name)

class hqpornerListScreen(MPScreen, ThumbsHelper):

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

		self['title'] = Label("HQPORNER")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))

		self.tw_agent_hlp = TwAgentHelper(followRedirect=True)
		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "http://hqporner.com/?s=%s&p=%s" % (self.Link, str(self.page))
		else:
			url = self.Link + "/" + str(self.page)
		getPage(url, agent=hqAgent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		if re.match('.*?NO RESULTS ON YOUR REQUEST', data, re.S|re.I):
			self.filmliste.append((_('No movies found!'), None, None, None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
		else:
			self.getLastPage(data, 'pagination">(.*?)</ul>')
			parse = re.search('<div\sclass="box\spage-content">\s+(.*?)pagination', data, re.S)
			raw = re.findall('section\sclass="box\sfeature">\s+<a href="(.*?)".*?\ssrc="(.*?)"\salt="(.*?)".*?fa-clock-o meta-data">(.*?)<', parse.group(1), re.S)
			if raw:
				for (link, image, title, age) in raw:
					link = "http://hqporner.com" + link
					if image.startswith('//'):
						image = 'http:' + image
					title = title.title()
					self.filmliste.append((decodeHtml(title), link, image, age))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)
		coverUrl = self['liste'].getCurrent()[0][2]
		age = self['liste'].getCurrent()[0][3]
		self['handlung'].setText("Runtime: %s" % age)
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link == None:
			return
		getPage(Link, agent=hqAgent, headers={'Referer': 'http://hqporner.com'}).addCallback(self.get_url).addErrback(self.dataError)

	def get_url(self, data):
		Link = re.findall('<iframe\swidth="\d+"\sheight="\d+"\ssrc="((?:http:|)//(.*?)\/.*?)"', data, re.S)
		if Link:
			if Link[0][0].startswith('//'):
				url = 'http:' + Link[0][0]
			else:
				url = Link[0][0]
			if re.match('.*?//hqporner.com', url):
				getPage(url, agent=hqAgent).addCallback(self.getVideoLink).addErrback(self.dataError)
			elif re.match('.*?//bemywife\.cc', url):
				getPage(url, agent=hqAgent).addCallback(self.bemywife).addErrback(self.dataError)
			elif re.match('.*?//mydaddy\.cc', url):
				getPage(url, agent=hqAgent).addCallback(self.mydaddy).addErrback(self.dataError)
			elif re.match('.*?//hqwo\.cc', url):
				getPage(url, agent=hqAgent).addCallback(self.leaseweb).addErrback(self.dataError)
			elif re.match('.*?//5\.79\.64\.169', url):
				getPage(url, agent=hqAgent).addCallback(self.leaseweb).addErrback(self.dataError)
			elif isSupportedHoster(Link[0][1].replace('www.',''), True):
				get_stream_link(self.session).check_link(url, self.got_link)
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)

	def bemywife(self, data):
		stream_url = re.findall('file:\s"(.*?(\d+).mp4)"', data, re.S)
		if stream_url:
			stream_url.sort(key=lambda t : t[1], reverse=False)
			if 'http://' in stream_url[-1][0]:
				link = stream_url[-1][0]
			else:
				link = "http://bemywife.cc" + stream_url[-1][0]
			self.got_link(link)
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)

	def mydaddy(self, data):
		stream_url = re.findall('file:\s"(.*?(\d+).mp4)"', data)
		if stream_url:
			stream_url.sort(key=lambda t : t[1], reverse=False)
			if stream_url[-1][0].startswith('//'):
				link = 'http:' + stream_url[-1][0]
			else:
				link = stream_url[-1][0]
			self.got_link(link)
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)

	def leaseweb(self, data):
		stream_url = re.findall('src=["|\'](http://[A-Za-z0-9\.]+/runplayer/.*?)["|\']', data, re.S)
		if stream_url:
			getPage(stream_url[0], agent=hqAgent).addCallback(self.leaseweblink).addErrback(self.dataError)
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)

	def leaseweblink(self, data):
		stream_url = re.findall('file":\s"(.*?mp4)"', data, re.S)
		if stream_url:
			self.got_link(stream_url[-1])
		else:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)

	def getVideoLink(self, data):
		get_packedjava = re.findall("<script type=.text.javascript.>(eval.function.*?)</script>", data, re.S)
		if get_packedjava and detect(get_packedjava[0]):
			sJavascript = re.sub("\}\}\)\}\);',\d+,", "}})});',62,", get_packedjava[0])
			sUnpacked = unpack(sJavascript)
			if sUnpacked:
				videoIDs = re.findall("oid:.'(.*?).',video_id:.'(.*?).',embed_hash:.'(.*?).'", sUnpacked, re.S)
				if videoIDs:
					stream = "https://api.vk.com/method/video.getEmbed?oid=%s&video_id=%s&embed_hash=%s&callback=callbackFunc" % (videoIDs[0][0],videoIDs[0][1],videoIDs[0][2])
					get_stream_link(self.session).check_link(stream, self.got_link)

	def got_link(self, stream_url):
		Title = self['liste'].getCurrent()[0][0]
		self['name'].setText(Title)
		self.session.open(SimplePlayer, [(Title, stream_url)], showPlaylist=False, ltype='hqporner')