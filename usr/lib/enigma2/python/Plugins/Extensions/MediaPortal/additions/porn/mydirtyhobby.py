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
from Plugins.Extensions.MediaPortal.resources.DelayedFunction import DelayedFunction

myagent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'

mdh_ck = {}
mdh_cookies = CookieJar()

default_cover = "file://%s/mydirtyhobby.png" % (config.mediaportal.iconcachepath.value + "logos")

class MDHGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("MyDirtyHobby")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self['name'].setText(_("Please wait..."))
		url = "http://stream-mydirtyhobby.biz"
		getPage(url, agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.checkData).addErrback(self.dataError)

	def checkData(self, data):
		if "XMLHttpRequest" in data:
			parse = re.findall('GET","(.*?)".*?"(.*?)"', data, re.S)
			url = "http://stream-mydirtyhobby.biz" + parse[0][0] + str(random.randint(1400,1800)) + parse[0][1]
			DelayedFunction(4000, self.getJs, url)
		elif 'class="g-recaptcha"' in data:
			self['name'].setText('')
			self.session.open(MessageBoxExt, _("Google reCAPTCHA detected, please verify your current IP by\naccessing the website 'http://stream-mydirtyhobby.biz' with your browser."), MessageBoxExt.TYPE_INFO)
		else:
			self.genreData(data)

	def getJs(self, url):
		getPage(url, agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.getJs2).addErrback(self.dataError)

	def getJs2(self, data):
		try:
			import execjs
			node = execjs.get("Node")
		except:
			printl('nodejs not found',self,'E')
			self.session.open(MessageBoxExt, _("This plugin requires packages python-pyexecjs and nodejs."), MessageBoxExt.TYPE_INFO)
			return
		js = re.search('(.*?)if\(\$\(window', data, re.S).group(1)
		js = js + "function go(){ cookie = toHex(BFCrypt.decrypt(c, 2, a, b)) };"
		js = js + 'go(); return cookie;'
		result = node.exec_(js)
		printl('BLAZINGFAST-WEB-PROTECT: '+result,self,'A')
		mdh_ck.update({'BLAZINGFAST-WEB-PROTECT':str(result)})
		url = "http://stream-mydirtyhobby.biz/empty"
		getPage(url, agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.genreData).addErrback(self.genreData)

	def genreData(self, data=None):
		self['name'].setText('')
		self.genreliste.insert(0, ("Most Commented", "http://stream-mydirtyhobby.biz/channel/video/general?page=%s&filter=comments"))
		self.genreliste.insert(0, ("Most Viewed", "http://stream-mydirtyhobby.biz/channel/video/general?page=%s&filter=views"))
		self.genreliste.insert(0, ("Most Popular", "http://stream-mydirtyhobby.biz/channel/video/general?page=%s&filter=likes"))
		self.genreliste.insert(0, ("Newest", "http://stream-mydirtyhobby.biz/channel/video/general?page=%s&filter=date"))
		self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		else:
			self.session.open(MDHFilmScreen, Link, Name)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			Name = "--- Search ---"
			self.suchString = callback
			Link = self.suchString.replace(' ', '%20')
			self.session.open(MDHFilmScreen, Link, Name)

class MDHFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr', default_cover=default_cover)
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"5" : self.keyShowThumb,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("MyDirtyHobby")
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
			url = "http://stream-mydirtyhobby.biz/search/%s?page=%s" % (self.Link, str(self.page))
		else:
			url = self.Link % str(self.page)
		getPage(url, agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class="pager">(.*?)</div>', '.*[>|=](\d+)[<|&|"]')
		parse = re.search("(.*?)id='sidebar_categories'>", data, re.S)
		Movies = re.findall("class='mediathumb'.*?ref='(.*?)'.*?class='mediabg'.*?url\((.*?)\)'>(.*?)</span>.*?'mediadate'>(.*?)</span>.*?'mediaviews'>(\d+,{0,1}\d+).*?</span>", parse.group(1), re.S)
		if Movies:
			for (Url, Image, Title, Added, Views) in Movies:
				self.filmliste.append((decodeHtml(Title), Url, Image, Views, Added))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No videos found!'), '', None, '', ''))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1, agent=myagent, cookies=mdh_ck)
		self.showInfos()
		self.keyLocked = False

	def showInfos(self):
		title = self['liste'].getCurrent()[0][0]
		pic = self['liste'].getCurrent()[0][2]
		views = self['liste'].getCurrent()[0][3].replace(',','')
		added = self['liste'].getCurrent()[0][4]
		self['name'].setText(title)
		self['handlung'].setText("Views: %s\nAdded: %s" % (views, added))
		import requests
		requests.cookies.cookiejar_from_dict(mdh_ck, cookiejar=mdh_cookies)
		CoverHelper(self['coverArt']).getCover(pic, agent=myagent, cookieJar=mdh_cookies)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		self.keyLocked = True
		getPage(Link, agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.getVideoUrl).addErrback(self.dataError)

	def getVideoUrl(self, data):
		url = re.findall("iframe\ssrc='(.*?)'", data, re.S|re.I)
		if url:
			getPage(url[0], agent=myagent, cookies=mdh_ck, headers={'Referer':'http://stream-mydirtyhobby.biz/'}).addCallback(self.getVideoUrl2).addErrback(self.dataError)
		else:
			self.keyLocked = False

	def getVideoUrl2(self, data):
		url = re.findall('iframe\ssrc="(.*?)"', data, re.S|re.I)
		if url:
			get_stream_link(self.session).check_link(url[0], self.got_link)
			self.keyLocked = False

	def got_link(self, url):
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, url)], showPlaylist=False, ltype='mydirtyhobby')