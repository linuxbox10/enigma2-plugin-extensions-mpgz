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
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage
import base64

glob_cookies = CookieJar()
myagent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.46 Safari/535.11'
BASE_URL = 'http://streamxxx.tv'

class streamxxxGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("StreamXXX")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.genreData)

	def genreData(self):
		self.genreliste.append(("--- Search ---", None))
		self.genreliste.append(("Newest", "%s/" % BASE_URL))
		self.genreliste.append(("Category", "Category"))
		self.genreliste.append(("Networks", "Networks"))
		self.genreliste.append(("Movies", "%s/category/movies-xxx/" % BASE_URL))
		self.genreliste.append(("International Movies", "%s/category/movies/international-movies/" % BASE_URL))
		self.genreliste.append(("German Movies", "%s/category/international-movies/?s=german" % BASE_URL))
		self.genreliste.append(("French Movies", "%s/category/international-movies/?s=french" % BASE_URL))
		self.genreliste.append(("Italian Movies", "%s/category/movies/film-porno-italian/" % BASE_URL))
		self.genreliste.append(("Cento-X-Cento", "%s/tag/cento-x-cento/" % BASE_URL))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			Link = self.suchString
			Name = self['liste'].getCurrent()[0][0]
			self.session.open(streamxxxFilmScreen, Link, Name)

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if Name == "--- Search ---":
			self.suchen()
		elif Name == "Networks" or Name == "Category":
			self.session.open(streamxxxSubGenreScreen, Link, Name)
		else:
			self.session.open(streamxxxFilmScreen, Link, Name)

class streamxxxSubGenreScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("StreamXXX")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''
		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		twAgentGetPage(BASE_URL, agent=myagent).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		if self.Link == "Category":
			preparse = re.search('>TOP TAGS(.*?)</ul>', data, re.S|re.I)
			if preparse:
				parse = re.findall('href="(.*?)">(.*?)</a', preparse.group(1), re.S)
		else:
			preparse = re.search('>BEST NETWORKS</h4>(.*?)</div>', data, re.S|re.I)
			if preparse:
				parse = re.findall('href="(.*?)"(?: rel="tag"|)>(.*?)</a', preparse.group(1), re.S)
		if parse:
			for (Url, Title) in parse:
				Title = Title.lower().title()
				if not re.match('http', Url):
					Url = "%s%s" % (BASE_URL, Url)
				self.genreliste.append((decodeHtml(Title), Url))
			self.genreliste.sort()
		if len(self.genreliste) == 0:
			self.filmliste.append((_('Nothing found!'), ''))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False
		self['name'].setText("")

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(streamxxxFilmScreen, Link, Name)

class streamxxxFilmScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
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

		self['title'] = Label("StreamXXX")
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
		self['name'].setText(_('Please wait...'))
		self.keyLocked = True
		self.filmliste = []
		if re.match(".*?Search", self.Name):
			url = "%s/page/%s/?s=%s" % (BASE_URL, str(self.page), self.Link)
		elif re.search('/\?s=', self.Link):
			urlpart = self.Link.split("?s=")
			url = "%spage/%s/?s=%s" % (urlpart[0],str(self.page),urlpart[1])
		else:
			url = self.Link + "page/" + str(self.page) + "/"
		twAgentGetPage(url, agent=myagent).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		self.getLastPage(data, 'class=\'page-numbers\'>(.*?)</ul>', '.*>((?:\d+.)\d+)<')
		Movies = re.findall('<article\sid="post-\d+.*?<a\shref="(.*?)"\stitle="(.*?)".*?<img src="(.*?)".*?(\d+)\sViews', data, re.S)
		if Movies:
			for (Url, Title, Image, Views) in Movies:
				if not re.match('http', Url):
					Url = BASE_URL + "/" + Url
				self.filmliste.append((decodeHtml(Title), Url, Image, Views))
		if len(self.filmliste) == 0:
			self.filmliste.append((_('No movies found!'), None, None, None, None))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.th_ThumbsQuery(self.filmliste, 0, 1, 2, None, None, self.page, self.lastpage, mode=1)
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		Views = self['liste'].getCurrent()[0][3]
		handlung = "Views: %s" % (Views)
		self['name'].setText(Title)
		self['handlung'].setText(decodeHtml(handlung))
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Title = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		Image = self['liste'].getCurrent()[0][2]
		if Link == None:
			return
		self.session.open(streamxxxStreamListeScreen, Link, Title, Image)

class streamxxxStreamListeScreen(MPScreen):

	def __init__(self, session, streamFilmLink, streamName, streamImage):
		self.streamFilmLink = streamFilmLink
		self.streamName = streamName
		self.streamImage = streamImage
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("StreamXXX")
		self['ContentTitle'] = Label("Streams:")
		self['name'] = Label(_("Please wait..."))

		self.captchainfo = {}
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		CoverHelper(self['coverArt']).getCover(self.streamImage)
		self.keyLocked = True
		self.filmliste = []
		twAgentGetPage(self.streamFilmLink, cookieJar=glob_cookies, agent=myagent).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('class="stream">(.*?)</div>', data, re.S)
		streams = re.findall('(http[s]?://(.*?)\/.*?)[\'|"|\&|<]', parse.group(1), re.S)
		if streams:
			for (stream, hostername) in streams:
				if isSupportedHoster(hostername, True):
					hostername = hostername.replace('www.','')
					self.filmliste.append((hostername, stream))
		if len(self.filmliste) == 0:
			if re.search('data:image/jpeg;base64', data,re.S):
				self.getCaptchaCookie(data)
			else:
				self.filmliste.append((_("No supported streams found!"), None))
		self.filmliste = list(set(self.filmliste))
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self.keyLocked = False
		self['name'].setText(self.streamName)

	def getCaptchaCookie(self, data):
		p1 = re.search('content-protector-token.*?value="(.*?)"', data, re.S)
		p2 = re.search('content-protector-ident-(.*?)"', data, re.S)
		p3 = re.search('src="data:image/jpeg;base64,(.*?)"', data, re.S)
		if p1 and p2 and p3:
			jpgfile = ('/tmp/captcha.jpg')
			g = open(jpgfile, "w")
			g.write(base64.decodestring(p3.group(1)))
			g.close()
			self.captchainfo = {
				'content-protector-expires': "0",
				'content-protector-token': p1.group(1),
				'content-protector-ident': p2.group(1),
				'content-protector-submit':'Submit'
				}
			self.session.openWithCallback(self.captchaCallback, VirtualKeyBoardExt, title = (_("Captcha input:")), text = "", captcha = "/tmp/captcha.jpg", is_dialog=True)

	def captchaCallback(self, callback=None, entry=None):
		if callback != None or callback != "":
			self.captchainfo.update({'content-protector-password': callback})
			twAgentGetPage(self.streamFilmLink, cookieJar=glob_cookies, method='POST', postdata=urlencode(self.captchainfo), agent=myagent, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if url:
			get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.streamName, stream_url, self.streamImage)], showPlaylist=False, ltype='streamxxx', cover=True)