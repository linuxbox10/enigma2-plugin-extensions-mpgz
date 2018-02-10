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
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage
from Plugins.Extensions.MediaPortal.resources.pininputext import PinInputExt

config.mediaportal.movie4klang2 = ConfigText(default="de", fixed_size=False)
config.mediaportal.movie4kdomain3 = ConfigText(default="http://movie4k.me", fixed_size=False)

m4k = config.mediaportal.movie4kdomain3.value.replace('https://','').replace('http://','')
m4k_url = "%s/" % config.mediaportal.movie4kdomain3.value
g_url = "%s/movies-genre-" % config.mediaportal.movie4kdomain3.value

ds = defer.DeferredSemaphore(tokens=1)

try:
	from Plugins.Extensions.MediaPortal.resources import cfscrape
except:
	cfscrapeModule = False
else:
	cfscrapeModule = True

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

import urlparse
import thread

m4k_cookies = CookieJar()
m4k_ck = {}
m4k_agent = ''

def m4kcancel_defer(deferlist):
	try:
		[x.cancel() for x in deferlist]
	except:
		pass

class m4kGenreScreen(MPScreen):

	def __init__(self, session, mode=""):
		self.showM4kPorn = mode
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"yellow" : self.keyLocale,
			"blue" : self.keyDomain,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self.locale = config.mediaportal.movie4klang2.value
		self.domain = config.mediaportal.movie4kdomain3.value

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("Genre:")
		if self.showM4kPorn != "porn":
			self['F3'] = Label(self.locale)
		self['F4'] = Label(self.domain)

		self.searchStr = ''
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.pin = False
		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		m4k_ck.clear()
		self.keyLocked = True
		thread.start_new_thread(self.get_tokens,("GetTokens",))
		self['name'].setText(_("Please wait..."))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global m4k_ck
			global m4k_agent
			if m4k_ck == {} or m4k_agent == '':
				m4k_ck, m4k_agent = cfscrape.get_tokens(m4k_url)
				requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
			else:
				s = requests.session()
				url = urlparse.urlparse(m4k_url)
				headers = {'user-agent': m4k_agent}
				page = s.get(url.geturl(), cookies=m4k_cookies, headers=headers, allow_redirects=False)
				if page.status_code == 503 and page.headers.get("Server") == "cloudflare-nginx":
					m4k_ck, m4k_agent = cfscrape.get_tokens(m4k_url)
					requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
			if self.locale == "de":
				m4k_ck.update({'lang':'de'})
				requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
			elif self.locale == "en":
				m4k_ck.update({'lang':'en'})
				requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
			self.keyLocked = False
			reactor.callFromThread(self.getGenres)
		else:
			reactor.callFromThread(self.m4k_error)

	def m4k_error(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or python-pyexecjs and nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def getGenres(self):
		self.list = []
		if self.showM4kPorn == "porn":
			self.list.append(("Letzte Updates", m4k_url+"xxx-updates.html"))
			self.list.append(('Genres', m4k_url+"genres-xxx.html"))
			self.list.append(("Alle Filme A-Z", "XXXAZ"))
		else:
			self.list.append(("Kinofilme", m4k_url+"index.php"))
			self.list.append(("Videofilme", m4k_url+"index.php"))
			self.list.append(("Letzte Updates", m4k_url+"index.php"))
			self.list.append(("Alle Filme A-Z", "FilmeAZ"))
			self.list.append(("Suche...", m4k_url+"movies.php?list=search"))
			self.list.append(("Abenteuer", g_url+"4-"))
			self.list.append(("Action", g_url+"1-"))
			self.list.append(("Biografie", g_url+"6-"))
			self.list.append(("Bollywood", g_url+"27-"))
			self.list.append(("Dokumentation", g_url+"8-"))
			self.list.append(("Drama", g_url+"2-"))
			self.list.append(("Erwachsene", g_url+"58-"))
			self.list.append(("Familie", g_url+"9-"))
			self.list.append(("Fantasy", g_url+"10-"))
			self.list.append(("Geschichte", g_url+"13-"))
			self.list.append(("Horror", g_url+"14-"))
			self.list.append(("Komödie", g_url+"3-"))
			self.list.append(("Kriegsfilme", g_url+"24-"))
			self.list.append(("Krimi", g_url+"7-"))
			self.list.append(("Kurzfilme", g_url+"55-"))
			self.list.append(("Musicals", g_url+"56-"))
			self.list.append(("Musik", g_url+"15-"))
			self.list.append(("Mystery", g_url+"17-"))
			self.list.append(("Reality TV", g_url+"59-"))
			self.list.append(("Romantik", g_url+"20-"))
			self.list.append(("Sci-Fi", g_url+"21-"))
			self.list.append(("Sport", g_url+"22-"))
			self.list.append(("Thriller", g_url+"23-"))
			self.list.append(("Trickfilm", g_url+"5-"))
			self.list.append(("Western", g_url+"25-"))
		self.ml.setList(map(self._defaultlistcenter, self.list))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		if self.keyLocked:
			return
		name = self['liste'].getCurrent()[0][0]
		self.url = self['liste'].getCurrent()[0][1]
		if name == "Kinofilme":
			self.session.open(m4kFilme, self.url, name)
		elif name == "Videofilme":
			self.session.open(m4kFilme, self.url, name)
		elif "xxx-updates.html" in self.url:
			self.session.open(m4kXXXListeScreen, self.url, name, '')
		elif name == "Letzte Updates":
			self.session.open(m4kupdateFilme, self.url, name)
		elif "Alle Filme A-Z" in name:
			self.session.open(m4kABCAuswahl, self.url, name)
		elif name == "Suche...":
			self.session.openWithCallback(self.searchCallback, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = "", is_dialog=True)
		elif name == "Erwachsene":
			if config.mediaportal.pornpin.value and not self.pin:
				self.pincheck()
			else:
				self.session.open(m4kKinoAlleFilmeListeScreen, self.url, name)
		else:
			self.session.open(m4kKinoAlleFilmeListeScreen, self.url, name)

	def pincheck(self):
		self.session.openWithCallback(self.pincheckok, PinInputExt, pinList = [(config.mediaportal.pincode.value)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct PIN"), windowTitle = _("Enter PIN"))

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pincheckok(self, pincode):
		if pincode:
			self.pin = True
			self.keyOK()

	def keyDomain(self):
		if self.domain == "https://movie4k.am":
			config.mediaportal.movie4kdomain3.value = "https://movie.to"
		elif self.domain == "https://movie.to":
			config.mediaportal.movie4kdomain3.value = "http://movie4k.pe"
		elif self.domain == "http://movie4k.pe":
			config.mediaportal.movie4kdomain3.value = "https://movie4k.tv"
		elif self.domain == "https://movie4k.tv":
			config.mediaportal.movie4kdomain3.value = "http://movie4k.me"
		elif self.domain == "http://movie4k.me":
			config.mediaportal.movie4kdomain3.value = "http://movie4k.org"
		elif self.domain == "http://movie4k.org":
			config.mediaportal.movie4kdomain3.value = "https://movie4k.am"
		else:
			config.mediaportal.movie4kdomain3.value = "http://movie4k.me"
		config.mediaportal.movie4kdomain3.save()
		configfile.save()
		self.domain = config.mediaportal.movie4kdomain3.value
		global m4k, m4k_url, g_url
		m4k = "%s" % self.domain.replace('https://','').replace('http://','')
		m4k_url = "%s/" % self.domain
		g_url = "%s/movies-genre-" % self.domain
		self['title'].setText(m4k)
		self['F4'].setText(self.domain)
		self.layoutFinished()

	def keyLocale(self):
		if self.showM4kPorn != "porn":
			global m4k_ck
			if self.locale == "de":
				m4k_ck.update({'lang':'de'})
				requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
				self.locale = "en"
				config.mediaportal.movie4klang2.value = "en"
			elif self.locale == "en":
				m4k_ck.update({'lang':'en'})
				requests.cookies.cookiejar_from_dict(m4k_ck, cookiejar=m4k_cookies)
				self.locale = "de"
				config.mediaportal.movie4klang2.value = "de"
			config.mediaportal.movie4klang2.save()
			configfile.save()
			self['F3'].setText(self.locale)
			self.layoutFinished()

	def searchCallback(self, callbackStr):
		if callbackStr is not None:
			self.searchStr = callbackStr
			self.searchData = self.searchStr
			self.session.open(m4kSucheAlleFilmeListeScreen, self.url, self.searchData)

class m4kSucheAlleFilmeListeScreen(MPScreen):

	def __init__(self, session, searchUrl, searchData):
		self.searchUrl = searchUrl
		self.searchData = searchData
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("Suche nach: %s" % self.searchData)

		self.deferreds = []
		self.keyLocked = True
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_("Please wait..."))
		url = "%s&search=%s" % (self.searchUrl, self.searchData)
		twAgentGetPage(url, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		kino = re.findall('<TR id="coverPreview(.*?)">.*?<a href="(.*?)">(.*?)<', data, re.S)
		if kino:
			self.list = []
			for image, teil_url, title in kino:
				url = '%s%s' % (m4k_url, teil_url)
				self.list.append((decodeHtml(title), url, image))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		self['name'].setText(streamName)
		m4kcancel_defer(self.deferreds)
		downloads = ds.run(twAgentGetPage, streamUrl, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.showHandlung).addErrback(self.dataError)
		self.deferreds.append(downloads)

	def showHandlung(self, data):
		filmdaten = re.findall('<div style="float:left">.*?<img src="(.*?)".*?<div class="moviedescription">(.*?)</div>', data, re.S)
		if filmdaten:
			streamPic, handlung = filmdaten[0]
			CoverHelper(self['coverArt']).getCover(streamPic, agent=m4k_agent, cookieJar=m4k_cookies)
			self['handlung'].setText(decodeHtml(handlung).strip())

	def keyOK(self):
		if self.keyLocked:
			return
		streamGenreName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		self.session.open(m4kStreamListeScreen, streamLink, streamGenreName)

class m4kKinoAlleFilmeListeScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		if not "genres-xxx.html" in self.streamGenreLink:
			self["actions2"] = ActionMap(["MP_Actions"], {
				"green" : self.keyPageNumber
			}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("Filme Auswahl: %s" % self.streamGenreName)
		if not "genres-xxx.html" in self.streamGenreLink:
			self['F2'] = Label(_("Page"))

		self.deferreds = []
		self.keyLocked = True
		self.preview = False
		self.XXX = False
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.page = 1
		self.lastpage = 1

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		if self.streamGenreLink == '%sgenres-xxx.html' % m4k_url:
			twAgentGetPage(self.streamGenreLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadXXXPageData).addErrback(self.dataError)
		elif re.search('%sxxx' % m4k_url, self.streamGenreLink):
			url = '%s%s%s' % (self.streamGenreLink, self.page, '.html')
			twAgentGetPage(url, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)
		elif re.search('http[s]?://(www.|)movie[^/]+/movies-(updates|all|genre)-', self.streamGenreLink):
			url = '%s%s%s' % (self.streamGenreLink, self.page, '.html')
			twAgentGetPage(url, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)
		else:
			twAgentGetPage(self.streamGenreLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadXXXPageData(self, data):
		self.XXX = True
		xxxGenre = re.findall('<TD\sid="tdmovies"\swidth="155">.*?<a\shref="(xxx-genre.*?)">(.*?)</a>', data, re.S)
		if xxxGenre:
			self.list = []
			for teil_url, title in xxxGenre:
				url = '%s%s' % (m4k_url, teil_url)
				title = title.replace("\t","")
				title = title.strip(" ")
				self.list.append((decodeHtml(title), url))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def loadPageData(self, data):
		self['Page'].setText(_("Page:"))
		self.getLastPage(data, 'id="boxwhite"(.*?)<br>', '.*>(\d+)\s<')
		kino = re.findall('<TR id="coverPreview(.*?)">.*?<a href="(.*?)">(.*?)</a>', data, re.S)
		self.preview = False
		if re.search('hover\(function\(e\)', data, re.S):
			self.preview = True
		if kino:
			self.list = []
			for image, teil_url, title in kino:
				url = '%s%s' % (m4k_url, teil_url)
				if self.preview == True:
					imagelink = re.findall('coverPreview%s"\).hover\(.*?<img src=\'(.*?)\' alt' % image, data, re.S)
					if imagelink:
						self.list.append((decodeHtml(title).strip(), url, imagelink[0]))
					else:
						self.list.append((decodeHtml(title).strip(), url, None))
				else:
					self.list.append((decodeHtml(title).strip(), url, None))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), None, None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		streamUrl = self['liste'].getCurrent()[0][1]
		self['name'].setText(streamName)
		m4kcancel_defer(self.deferreds)
		downloads = ds.run(twAgentGetPage, streamUrl, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.showHandlung).addErrback(self.dataError)
		self.deferreds.append(downloads)

	def showHandlung(self, data):
		filmdaten = re.findall('<div style="float:left">.*?<img src="(.*?)".*?<div class="moviedescription">(.*?)</div>', data, re.S)
		if filmdaten:
			streamPic, handlung = filmdaten[0]
			CoverHelper(self['coverArt']).getCover(streamPic, agent=m4k_agent, cookieJar=m4k_cookies)
			self['handlung'].setText(decodeHtml(handlung).strip())

	def keyOK(self):
		if self.keyLocked:
			return
		if self.XXX == False:
			streamGenreName = self['liste'].getCurrent()[0][0]
			streamLink = self['liste'].getCurrent()[0][1]
			self.session.open(m4kStreamListeScreen, streamLink, streamGenreName)
		else:
			streamGenreName= self['liste'].getCurrent()[0][0]
			xxxGenreLink = self['liste'].getCurrent()[0][1]
			self.session.open(m4kXXXListeScreen, xxxGenreLink, streamGenreName, 'X')

class m4kupdateFilme(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("Filme Auswahl: %s" % self.streamGenreName)

		self.deferreds = []
		self.keyLocked = True
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_("Please wait..."))
		twAgentGetPage(self.streamGenreLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('">(?:Letzte|Latest) Updates(.*?)id="maincontent">', data, re.S)
		if parse:
			last = re.findall('<td\svalign="top"\sheight="100%"><a\shref="(.*?)".{0,1}><font\scolor="#000000"\ssize="-1"><strong>(.*?)</strong></font></a></td>', parse.group(1), re.S)
			if last:
				for url,title in last:
					url = "%s%s" % (m4k_url, url)
					self.list.append((decodeHtml(title), url))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamUrl = self['liste'].getCurrent()[0][1]
		if streamUrl:
			m4kcancel_defer(self.deferreds)
			downloads = ds.run(twAgentGetPage, streamUrl, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.showHandlung).addErrback(self.dataError)
			self.deferreds.append(downloads)

	def showHandlung(self, data):
		image = re.search('<img\ssrc="(http[s]?.*?/thumbs/.*?movie4k-film.jpg)"\sborder=0', data, re.S)
		if image:
			image = image.group(1)
			CoverHelper(self['coverArt']).getCover(image, agent=m4k_agent, cookieJar=m4k_cookies)
		handlung = re.findall('<div class="moviedescription">(.*?)<', data, re.S)
		if handlung:
			handlung = re.sub(r"\s+", " ", handlung[0])
			self['handlung'].setText(decodeHtml(handlung).strip())
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		self.session.open(m4kStreamListeScreen, streamLink, streamName)

class m4kFilme(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("Filme Auswahl: %s" % self.streamGenreName)

		self.deferreds = []
		self.keyLocked = True
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		twAgentGetPage(self.streamGenreLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if self.streamGenreName == "Kinofilme":
			kino = re.findall('<div style="float:left">.*?<a href="(.*?)"><img src="(.*?)" border=\"{0,1}0\"{0,1} style="width:105px;max-width:105px;max-height:160px;min-height:140px;" alt=".*?kostenlos" title="(.*?).kostenlos"></a>', data, re.S)
		else:
			kino = re.findall('<div style="float: left;">.*?<a href="(.*?)"><img src="(.*?)" alt=".*?" title="(.*?)" border=\"{0,1}0\"{0,1} style="width:105px;max-width:105px;max-height:160px;min-height:140px;"></a>', data, re.S)
		if kino:
			for url,image,title in kino:
				url = "%s%s" % (m4k_url, url)
				self.list.append((decodeHtml(title), url, image))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamUrl = self['liste'].getCurrent()[0][1]
		if streamUrl:
			m4kcancel_defer(self.deferreds)
			downloads = ds.run(twAgentGetPage, streamUrl, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.showHandlung).addErrback(self.dataError)
			self.deferreds.append(downloads)
		streamPic = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(streamPic, agent=m4k_agent, cookieJar=m4k_cookies)

	def showHandlung(self, data):
		handlung = re.findall('<div class="moviedescription">(.*?)<', data, re.S)
		if handlung:
			handlung = re.sub(r"\s+", " ", handlung[0])
			self['handlung'].setText(decodeHtml(handlung).strip())
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		self.session.open(m4kStreamListeScreen, streamLink, streamName)

class m4kStreamListeScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamName):
		self.streamGenreLink = streamGenreLink
		self.streamName = streamName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label(_("Stream Selection"))

		self.deferreds = []
		self.coverUrl = None
		self.keyLocked = True
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_("Please wait..."))
		twAgentGetPage(self.streamGenreLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if re.match('.*?(/img/parts/teil1_aktiv.png|/img/parts/teil1_inaktiv.png|/img/parts/part1_active.png|/img/parts/part1_inactive.png)', data, re.S):
			self.session.open(m4kPartListeScreen, data, self.streamName)
			self.close()
		else:
			dupe = []
			hosters = re.findall('<tr id=.*?tablemoviesindex2.*?>(.*?)</td></tr>', data, re.S)
			if hosters:
				self.list = []
				for hoster_raw in hosters:
					hoster_data = re.findall('href.*?"(.*?)">(.*?)<img.*?&nbsp;(.*?)<', hoster_raw)
					if hoster_data:
						(h_url, h_date, h_name) = hoster_data[0]
						hoster_url = "%s%s" % (m4k_url, h_url.replace('\\',''))
						if not hoster_url in dupe:
							dupe.append(hoster_url)
							if isSupportedHoster(h_name, True):
								self.list.append((h_name, hoster_url, h_date))
			else:
				hosters = re.findall('<a target="_blank" href="(http[s]?://(.*?)/.*?)"', data, re.S)
				if not hosters:
					hosters = re.findall('<iframe src="(http[s]?://(.*?)/.*?)"', data, re.S)
				if hosters:
					(h_url, h_name) = hosters[0]
					h_name = h_name.split('.')[-2]
					h_name = h_name.lower().replace('faststream', 'rapidvideo').replace('fastvideo', 'rapidvideo')
					h_url = h_url.replace('faststream.in', 'rapidvideo.ws').replace('fastvideo.in', 'rapidvideo.ws')
					if re.search('(streamin|porntube4k|pandamovie|plashporn|porntorpia)', h_name)or isSupportedHoster(h_name, True):
						self.list.append((h_name.capitalize(), h_url, ""))
			if len(self.list) == 0:
				self.list.append(("No supported streams found.", '', '', '', ''))
			self.ml.setList(map(self._defaultlisthoster, self.list))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self.showInfosData(data)
			self['name'].setText(self.streamName)

	def showInfosData(self, data):
		image = re.search('<img\ssrc="(http[s]?.*?/thumbs/.*?movie4k-film.jpg)".*?class="moviedescription"', data, re.S)
		if image:
			image = image.group(1)
		else:
			image = None
		CoverHelper(self['coverArt']).getCover(image, agent=m4k_agent, cookieJar=m4k_cookies)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if isSupportedHoster(streamLink, True):
			get_stream_link(self.session).check_link(streamLink, self.got_link)
		else:
			twAgentGetPage(streamLink, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.get_streamlink, streamLink).addErrback(self.dataError)

	def get_streamlink(self, data, streamLink):
		link = re.search('<a\starget="_blank"\shref="(.*?)"><img\sborder=0\ssrc="/img/click_link.jpg"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\swidth=".*?"\sheight=".*?"\sframeborder="0"\ssrc="(.*?)"\sscrolling="no"></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\ssrc="(.*?)"\sframeborder=0\smarginwidth=0\smarginheight=0\sscrolling=no\swidth=.*?height=.*?></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search("<iframe\sstyle=.*?src='(.*?)'\sscrolling='no'></iframe>", data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<div\sid="emptydiv"><iframe.*?src=["|\'](.*?)["|\']', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<div\sid="emptydiv"><script type="text/javascript"\ssrc=["|\'](.*?)["|\']>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1).replace('?embed',''), self.got_link)
			return
		link = re.search('<object\sid="vbbplayer".*?src=["|\'](.*?)["|\']', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<param\sname="movie"\svalue="(.*?)"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<a target="_blank" href="(.*?)"><img border=0 src="/img/click_link.jpg"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\ssrc="(.*?)"\swidth=".*?"\sheight=".*?"\sframeborder="0"\sscrolling="no"></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('(http[s]?://o(pen)?load.co/embed/.*?)"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1).replace('oload.co', 'openload.co'), self.got_link)
			return
		message = self.session.open(MessageBoxExt, _("Stream not found, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=5)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBoxExt, _("Stream not found, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=3)
		else:
			self.session.open(SimplePlayer, [(self.streamName, stream_url, self.coverUrl)], showPlaylist=False, ltype='movie4k', cover=True)

class m4kPartListeScreen(MPScreen):

	def __init__(self, session, data, streamName):
		self.data = data
		self.streamName = streamName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label(_("Parts Selection"))
		self['name'] = Label(self.streamName)

		self.keyLocked = True
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		idnr = re.findall('<a href="((film|movie)\.php\?id=\d+&part=(\d+))', self.data, re.S)
		if idnr:
			for links in idnr:
				url = "%s%s" % (m4k_url, links[0])
				part = "Disk %s" % str(links[2])
				self.list.append((part, url))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), ''))
		self.ml.setList(map(self._defaultlistcenter, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		streamPart = self['liste'].getCurrent()[0][0]
		streamLinkPart = self['liste'].getCurrent()[0][1]
		self.sname = "%s - Teil %s" % (self.streamName, streamPart)
		twAgentGetPage(streamLinkPart, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.get_streamlink).addErrback(self.dataError)

	def get_streamlink(self, data):
		link = re.search('<a\starget="_blank"\shref="(.*?)"><img\sborder=0\ssrc="/img/click_link.jpg"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\swidth=".*?"\sheight=".*?"\sframeborder="0"\ssrc="(.*?)"\sscrolling="no"></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\ssrc="(.*?)"\sframeborder=0\smarginwidth=0\smarginheight=0\sscrolling=no\swidth=.*?height=.*?></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search("<iframe\sstyle=.*?src='(.*?)'\sscrolling='no'></iframe>", data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<div\sid="emptydiv"><iframe.*?src=["|\'](.*?)["|\']', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<div\sid="emptydiv"><script type="text/javascript"\ssrc=["|\'](.*?)["|\']>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1).replace('?embed',''), self.got_link)
			return
		link = re.search('<object\sid="vbbplayer".*?src=["|\'](.*?)["|\']', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<param\sname="movie"\svalue="(.*?)"', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return
		link = re.search('<iframe\ssrc="(.*?)"\swidth=".*?"\sheight=".*?"\sframeborder="0"\sscrolling="no"></iframe>', data, re.S|re.I)
		if link:
			get_stream_link(self.session).check_link(link.group(1), self.got_link)
			return

		message = self.session.open(MessageBoxExt, _("Stream not found, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=5)

	def got_link(self, stream_url):
		if stream_url == None:
			message = self.session.open(MessageBoxExt, _("Stream not found, try another Stream Hoster."), MessageBoxExt.TYPE_INFO, timeout=3)
		else:
			self.session.open(SimplePlayer, [(self.sname, stream_url)], showPlaylist=False, ltype='movie4k', cover=False)

class m4kXXXListeScreen(MPScreen):

	def __init__(self, session, streamXXXLink, streamGenreName, genre):
		self.streamXXXLink = streamXXXLink
		self.streamGenreName = streamGenreName
		self.genre = False
		if genre == 'X':
			self.genre = True
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"green" : self.keyPageNumber,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("XXX Auswahl")
		self['Page'].setText(_("Page:"))
		self['F2'] = Label(_("Page"))

		self.deferreds = []
		self.keyLocked = True
		self.preview = False
		self.page = 1
		self.lastpage = 1
		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		if self.genre == True:
			shortUrl = re.findall('%sxxx-genre-[0-9]*[0-9]*.*?' % m4k_url, self.streamXXXLink)
			shortUrlC = str(shortUrl[0])
			url = shortUrlC + '-' + str(self.page) + '.html'
		else:
			url = str(self.streamXXXLink)
		twAgentGetPage(url, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		self.getLastPage(data, 'id="boxwhite"(.*?)<br>', '.*>(\d+)\s<')
		self.list = []
		if self.genre == False:
			streams = re.findall('<TD id="(.*?)" width="380">.*?<a href="(.*?)">(.*?)</a>', data, re.S)
		else:
			streams = re.findall('<TR id="(.*?)">.*?<TD width="550" id="tdmovies">.*?<a href="(.*?)">(.*?)</a>', data, re.S)
		self.preview = False
		if re.search('hover\(function\(e\)', data, re.S):
			self.preview = True

		if streams:
			for cover,url,title in streams:
				url = "%s%s" % (m4k_url, url)
				title = title.replace("\t","")
				title = title.strip(" ")

				if self.preview == True:
					imagelink = re.findall('%s"\).hover\(.*?<img src=\'(.*?)\' alt' % cover, data, re.S)
					if imagelink:
						self.list.append((decodeHtml(title), url, imagelink[0]))
					else:
						self.list.append((decodeHtml(title), url, None))
				else:
					self.list.append((decodeHtml(title), url, None))
		if len(self.list) == 0:
			self.list.append((_('No movies found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.list))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamUrl = self['liste'].getCurrent()[0][1]
		m4kcancel_defer(self.deferreds)
		downloads = ds.run(twAgentGetPage, streamUrl, agent=m4k_agent, cookieJar=m4k_cookies, timeout=30).addCallback(self.showHandlung).addErrback(self.dataError)
		self.deferreds.append(downloads)

	def showHandlung(self, data):
		image = self['liste'].getCurrent()[0][2]
		if not image:
			image = re.search('<div style="float:left">.*?<img src="(.*?)".*?<div class="moviedescription">(.*?)</div>', data, re.S)
			if image:
				image = image.group(1)
			else:
				image = None
		elif not image.startswith('http'):
			image = m4k_url + image
		CoverHelper(self['coverArt']).getCover(image, agent=m4k_agent, cookieJar=m4k_cookies)
		handlung = re.findall('<div class="moviedescription">(.*?)<', data, re.S)
		if handlung:
			handlung = re.sub(r"\s+", " ", handlung[0])
			self['handlung'].setText(decodeHtml(handlung).strip())
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		self.session.open(m4kStreamListeScreen, streamLink, streamName)

class m4kABCAuswahl(MPScreen):

	def __init__(self, session, url, name):
		self.url = url
		self.name = name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"	: self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(m4k)
		self['ContentTitle'] = Label("%s" % self.name)

		self.keyLocked = True

		self.list = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.list = []
		abc = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","#"]
		for letter in abc:
			self.list.append((letter))
		self.ml.setList(map(self._defaultlistcenter, self.list))
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0]
		if auswahl == '#':
			auswahl = '1'
		if self.url == 'FilmeAZ':
			streamGenreName = "%s" % auswahl
			streamGenreLink = '%smovies-all-%s-' % (m4k_url, auswahl)
			self.session.open(m4kKinoAlleFilmeListeScreen, streamGenreLink, streamGenreName)
		elif self.url == 'XXXAZ':
			streamGenreName = "%s" % auswahl
			streamGenreLink = '%sxxx-all-%s-' % (m4k_url, auswahl)
			self.session.open(m4kKinoAlleFilmeListeScreen, streamGenreLink, streamGenreName)