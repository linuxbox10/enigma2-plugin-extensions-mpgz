# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper
from Components.ProgressBar import ProgressBar

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

BASE_URL = "https://streamit.ws"
sit_cookies = CookieJar()
sit_ck = {}
sit_agent = ''

def sit_grabpage(pageurl, method='GET', postdata={}):
	if requestsModule:
		try:
			s = requests.session()
			url = urlparse.urlparse(pageurl)
			headers = {'User-Agent': sit_agent}
			if method == 'GET':
				page = s.get(url.geturl(), cookies=sit_cookies, headers=headers)
			elif method == 'POST':
				page = s.post(url.geturl(), data=postdata, cookies=sit_cookies, headers=headers)
			return page.content
		except:
			pass

class showstreamitGenre(MenuHelper):

	base_menu = [
		(0, "/kino", 'Neu im Kino'),
		(0, "/film", 'Neueste Filme'),
		(0, "/film/?cat=1", 'Action'),
		(0, "/film/?cat=2", 'Adventure'),
		(0, "/film/?cat=3", 'Animation'),
		(0, "/film/?cat=4", 'Biography'),
		(0, "/film/?cat=5", 'Comedy'),
		(0, "/film/?cat=6", 'Crime'),
		(0, "/film/?cat=7", 'Documentary'),
		(0, "/film/?cat=8", 'Drama'),
		(0, "/film/?cat=9", 'Family'),
		(0, "/film/?cat=10", 'Fantasy'),
		(0, "/film/?cat=13", 'History'),
		(0, "/film/?cat=14", 'Horror'),
		(0, "/film/?cat=15", 'Music'),
		(0, "/film/?cat=17", 'Mystery'),
		(0, "/film/?cat=20", 'Romance'),
		(0, "/film/?cat=21", 'Sci-Fi'),
		(0, "/film/?cat=22", 'Sport'),
		(0, "/film/?cat=24", 'Thriller'),
		(0, "/film/?cat=25", 'War'),
		(0, "/film/?cat=26", 'Western'),
		]

	def __init__(self, session, m_level='main', m_path='/'):
		self.m_level = m_level
		self.m_path = m_path
		MenuHelper.__init__(self, session, 0, None, BASE_URL, "", self._defaultlistcenter, cookieJar=sit_cookies)

		self['title'] = Label("STREAMIT")
		self['ContentTitle'] = Label("Genres")
		self.param_search = ''
		self.search_token = None

		self.onLayoutFinish.append(self.mh_start)

	def mh_start(self):
		thread.start_new_thread(self.get_tokens,("GetTokens",))
		self['name'].setText(_("Please wait..."))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global sit_ck
			global sit_agent
			if sit_ck == {} or sit_agent == '':
				sit_ck, sit_agent = cfscrape.get_tokens(BASE_URL)
				requests.cookies.cookiejar_from_dict(sit_ck, cookiejar=sit_cookies)
			else:
				s = requests.session()
				url = urlparse.urlparse(BASE_URL)
				headers = {'user-agent': sit_agent}
				page = s.get(url.geturl(), cookies=sit_cookies, headers=headers)
				if page.status_code == 503 and page.headers.get("Server") == "cloudflare-nginx":
					sit_ck, sit_agent = cfscrape.get_tokens(BASE_URL)
					requests.cookies.cookiejar_from_dict(sit_ck, cookiejar=sit_cookies)
			reactor.callFromThread(self.mh_initMenu)
		else:
			reactor.callFromThread(self.mh_errorMenu)

	def mh_errorMenu(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or python-pyexecjs and nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def mh_initMenu(self):
		self.mh_buildMenu(self.mh_baseUrl + self.m_path, agent=sit_agent)

	def mh_parseCategorys(self, data):
		self.mh_genMenu2(self.base_menu)

	def mh_callGenreListScreen(self):
		genreurl = self.mh_baseUrl+self.mh_genreUrl[self.mh_menuLevel]
		self.session.open(streamitFilmListeScreen, genreurl, self.mh_genreTitle)

class streamitFilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName, series_img=None, last_series_tag='', season_data=None):
		self.genreLink = genreLink
		self.genreName = genreName
		self.seriesImg = series_img
		self.seasonData = season_data

		MPScreen.__init__(self, session, skin='MP_PluginDescr', widgets=('MP_widget_rating',))
		ThumbsHelper.__init__(self)

		self["hdpic"] = Pixmap()
		self['rating10'] = ProgressBar()
		self['rating0'] = Pixmap()
		self['bg_rating'] = Label()
		self["hdpic"].hide()

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"ok"    : self.keyOK,
			"cancel": self.keyCancel,
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
			"1" : self.key_1,
			"3" : self.key_3,
			"4" : self.key_4,
			"6" : self.key_6,
			"7" : self.key_7,
			"9" : self.key_9,
			"0": self.closeAll,
			"yellow" : self.keySort,
		}, -1)

		self.sortFuncs = None
		self.sortOrderStrGenre = ""
		self['title'] = Label("STREAMIT")

		self['Page'] = Label(_("Page:"))
		self['F3'] = Label(_("Sort by..."))
		self['F3'].hide()

		self.timerStart = False
		self.seekTimerRun = False
		self.eventL = threading.Event()
		self.eventH = threading.Event()
		self.eventP = threading.Event()
		self.filmQ = Queue.Queue(0)
		self.hanQ = Queue.Queue(0)
		self.picQ = Queue.Queue(0)
		self.updateP = 0
		self.keyLocked = True
		self.filmListe = []
		self.page = 0
		self.pages = 0;
		self.neueFilme = re.search('Neue Filme',self.genreName)
		self.sucheFilme = re.search('Videosuche',self.genreName)
		if 'HD Filme' in self.genreName:
			self.streamTag = 'streamhd'
		else:
			self.streamTag = 'stream'
		self.seriesTag = ''

		self.setGenreStrTitle()

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def setGenreStrTitle(self):
		if self.sortOrderStrGenre:
			sortOrder = ' (%s)' % self.sortOrderStrGenre
		else:
			sortOrder = ''

		self['ContentTitle'].setText("%s%s%s" % (self.seriesTag,self.genreName,sortOrder))

	def loadPage(self):
		if not self.sucheFilme and self.page > 1:
			page = max(1,self.page)
			link = self.genreLink
			if not '?' in link:
				link += '?'
			else:
				link += '&'
			url = "%spage=%d" % (link, page)
		else:
			url = self.genreLink

		if self.page:
			self['page'].setText("%d / %d" % (self.page,self.pages))

		self.filmQ.put(url)
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued()
		else:
			self['name'].setText(_('Please wait...'))
			self['handlung'].setText("")
			self['coverArt'].hide()

	def loadPageQueued(self):
		self['name'].setText(_('Please wait...'))
		self['handlung'].setText("")
		self['coverArt'].hide()
		while not self.filmQ.empty():
			url = self.filmQ.get_nowait()
		data = sit_grabpage(url)
		self.loadPageData(data)

	def dataError(self, error):
		self.eventL.clear()
		printl(error,self,"E")
		self.filmListe.append((_("No movies found!"),"","","", 0, False))
		self.ml.setList(map(self.streamitFilmListEntry,	self.filmListe))

	def loadPageData(self, data):
		self.getPostFuncs(data)
		self.filmListe = []
		l = len(data)
		a = 0
		while a < l:
			mg = re.search('<div class="post-thumb"(.*?)</div>\s+</li>', data[a:], re.S)
			if mg:
				a += mg.end()
				m = re.search('<a href="(.*?)".*?title="(.*?)">.*?<img.*?src="(.*?)".*?<div class="voting".*?style="width:(\d*)', mg.group(1), re.S)
				if m:
					url,name,imageurl,rating = m.groups()
					if 'hd_icon' in mg.group(1):
						hd = True
					else:
						hd = False

					if not rating: rating = "0"
					imdb = "IMDb: %.1f / 10" % (float(rating) / 10)
					if not url.startswith('http'):
						url = BASE_URL + url
					if not imageurl.startswith('http'):
						imageurl = BASE_URL + imageurl
					self.filmListe.append((decodeHtml(name), url, imageurl, imdb, rating, hd))
			else:
				a = l

		if self.filmListe:
			if not self.pages:
				m = re.search('class=\'pagination\'.*?page=(\d+)\'>Last</a', data)
				if m:
					self.pages = int(m.group(1))
				else:
					self.pages = 1

				self.page = 1
				self['page'].setText("%d / %d" % (self.page,self.pages))

			self.keyLocked = False
			self.ml.setList(map(self.streamitFilmListEntry,	self.filmListe))
			self.th_ThumbsQuery(self.filmListe, 0, 1, 2, None, None, self.page, self.pages, agent=sit_agent, cookies=sit_ck)

			self['liste'].moveToIndex(0)
			self.loadPicQueued()
		else:
			self.filmListe.append((_("No entries found!"),"","","", 0, False))
			self.ml.setList(map(self.streamitFilmListEntry,	self.filmListe))
			if self.filmQ.empty():
				self.eventL.clear()
			else:
				self.loadPageQueued()

	def getPostFuncs(self, data):
		self.sortFuncs = []
		try:
			m = re.search('id="postFuncs">(.*?)<!-- /#postFuncs -->', data, re.S)
			if m:
				for m2 in re.finditer('href="(.*?)">(.*?)</a', m.group(1)):
					href, name = m2.groups()
					href = re.sub('&page=\d+', '', href, 1)
					href = re.sub('\?page=\d+', '?', href, 1)
					self.sortFuncs.append((decodeHtml(name), decodeHtml(href)))
		except:
			pass
		if self.sortFuncs:
			self['F3'].show()
		else:
			self['F3'].hide()

	def loadPicQueued(self):
		self.picQ.put(None)
		if not self.eventP.is_set():
			self.eventP.set()
			self.loadPic()

	def loadPic(self):
		if self.picQ.empty():
			self.eventP.clear()
			return

		if self.eventH.is_set() or self.updateP:
			print "Pict. or descr. update in progress"
			print "eventH: ",self.eventH.is_set()
			print "eventP: ",self.eventP.is_set()
			print "updateP: ",self.updateP
			return

		while not self.picQ.empty():
			self.picQ.get_nowait()

		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		streamPic = self['liste'].getCurrent()[0][2]
		streamUrl = self['liste'].getCurrent()[0][1]
		self.updateP = 1
		CoverHelper(self['coverArt'], self.showCoverExit).getCover(streamPic, agent=sit_agent, cookieJar=sit_cookies)
		rate = self['liste'].getCurrent()[0][4]
		rating = int(rate)
		if rating > 100:
			rating = 100
		self['rating10'].setValue(rating)

	def dataErrorP(self, error):
		printl(error,self,"E")
		self.ShowCoverNone()

	def showCoverExit(self):
		self.updateP = 0;
		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
			self.loadPic()

	def keyOK(self):
		if self.keyLocked or self.eventL.is_set():
			return

		streamLink = self['liste'].getCurrent()[0][1]
		streamName = self['liste'].getCurrent()[0][0]
		imageLink = self['liste'].getCurrent()[0][2]
		self.session.open(streamitStreams, streamLink, streamName, imageLink, self.streamTag)

	def keyUpRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].up()

	def keyDownRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].down()

	def key_repeatedUp(self):
		if self.keyLocked:
			return
		self.loadPicQueued()

	def keyLeftRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].pageUp()

	def keyRightRepeated(self):
		if self.keyLocked:
			return
		self['coverArt'].hide()
		self['liste'].pageDown()

	def keyPageDown(self):
		if self.seekTimerRun:
			self.seekTimerRun = False
		self.keyPageDownFast(1)

	def keyPageUp(self):
		if self.seekTimerRun:
			self.seekTimerRun = False
		self.keyPageUpFast(1)

	def keyPageUpFast(self,step):
		if self.keyLocked:
			return
		oldpage = self.page
		if (self.page + step) <= self.pages:
			self.page += step
		else:
			self.page = 1
		if oldpage != self.page:
			self.loadPage()

	def keyPageDownFast(self,step):
		if self.keyLocked:
			return
		oldpage = self.page
		if (self.page - step) >= 1:
			self.page -= step
		else:
			self.page = self.pages
		if oldpage != self.page:
			self.loadPage()

	def key_1(self):
		self.keyPageDownFast(2)

	def key_4(self):
		self.keyPageDownFast(5)

	def key_7(self):
		self.keyPageDownFast(10)

	def key_3(self):
		self.keyPageUpFast(2)

	def key_6(self):
		self.keyPageUpFast(5)

	def key_9(self):
		self.keyPageUpFast(10)

	def keySort(self):
		if not self.keyLocked and self.sortFuncs:
			self.handleSort()

	def handleSort(self):
		self.session.openWithCallback(self.cb_handleSort, ChoiceBoxExt, title=_("Sort Selection"), list = self.sortFuncs)

	def cb_handleSort(self, answer):
		href = answer and answer[1]
		if href:
			self.genreLink = self.genreLink.split('?')[0] + href
			self.sortOrderStrGenre = answer[0]
			self.setGenreStrTitle()
			self.loadPage()

class streamitStreams(MPScreen):

	def __init__(self, session, filmUrl, filmName, imageLink, streamTag, post_data=None, post_url=None):
		self.filmUrl = filmUrl
		self.filmName = filmName
		self.imageUrl = imageLink
		self.stream_tag = streamTag
		self.postData = post_data
		self.postUrl = post_url

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"green" 	: self.keyTrailer,
			"ok"    	: self.keyOK,
			"0"		: self.closeAll,
			"cancel"	: self.keyCancel
		}, -1)

		self['title'] = Label("STREAMIT")
		self['ContentTitle'] = Label(_("Stream Selection"))

		self['name'] = Label(filmName)

		self.trailerId = None
		self.streamListe = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamListe.append((_('Please wait...'),"","",""))
		self.ml.setList(map(self.streamitStreamListEntry, self.streamListe))
		seriesStreams = self.postData != None
		data = sit_grabpage(self.filmUrl)
		self.parseData(data, seriesStreams)

	def getSeriesStreams(self):
		data = sit_grabpage(self.postUrl, method='POST', postdata=self.postData)
		self.parseStreams(data)

	def parseStreams(self, data):
		self.streamListe = []
		m = re.search('id="sel_qualideutsch">(.*?)</select>', data, re.S)
		if m:
			buttons = re.findall('id="(.*?)" class="mirrorbuttonsdeutsch">(.*?)</', m.group(1))
			for id,nm in buttons:
				m2 = re.search('class="mirrorsdeutsch"\sid="\w*%s"(.*?)></div></div>' % id, data, re.S)
				if m2:
					m3 = re.search('>Ton: <b>(.*?)</b', m2.group(1))
					if m3:
						ton = ', %s' % m3.group(1)
					else:
						ton = ''
					streams = re.findall('<a href="(.*?)".*?value="(.*?)"', m2.group(1).replace('\n', ''))
					for (isUrl,isStream) in streams:
						if isSupportedHoster(isStream, True):
							streamPart = ''
							isUrl = isUrl.replace('\n','')
							isUrl = isUrl.replace('\r','')
							self.streamListe.append((isStream,isUrl,streamPart,' (%s%s)' % (nm.strip(), ton.strip())))
						else:
							print "No supported hoster:"

		if self.streamListe:
			self.keyLocked = False
		else:
			self.streamListe.append(("No streams found!","","",""))
		self.ml.setList(map(self.streamitStreamListEntry, self.streamListe))

	def parseData(self, data, seriesStreams=False):
		m = re.search('//www.youtube\.com/(embed|v|p)/(.*?)(\?|" |&amp)', data)
		if m:
			self.trailerId = m.group(2)
			self['F2'].setText('Trailer')
		else: self.trailerId = None

		desc = ''
		mdesc = re.search('<b>(Jahr:)</b>.*?">(.*?)</.*?<b>(L&auml;nge:)</b>.*?">(.*?)</', data, re.S)
		if mdesc:
			desc += mdesc.group(1) + mdesc.group(2) + '  ' + mdesc.group(3) + mdesc.group(4) + '\n\n'
		elif desc:
			desc += '\n'

		mdesc = re.search('<div id="cleaner">&nbsp;</div><div id="cleaner">&nbsp;</div>(.*?)<br><br>',data, re.S)
		if mdesc:
			desc += re.sub('<.*?>', '', mdesc.group(1).replace('\n',''), re.S).replace('&nbsp;','').strip()
		else:
			desc += "Keine weiteren Info's !"

		self['handlung'].setText(decodeHtml(desc))
		CoverHelper(self['coverArt']).getCover(self.imageUrl, agent=sit_agent, cookieJar=sit_cookies)

		if not seriesStreams:
			self.parseStreams(data)
		else:
			self.getSeriesStreams()

	def dataError(self, error):
		printl(error,self,"E")
		self.streamListe.append(("Data error!","","",""))
		self.ml.setList(map(self.streamitStreamListEntry, self.streamListe))

	def gotLink(self, stream_url):
		if stream_url:
			title = self.filmName + self['liste'].getCurrent()[0][2]
			self.session.open(SimplePlayer, [(title, stream_url, self.imageUrl)], cover=True, showPlaylist=False, ltype='streamit')

	def keyTrailer(self):
		if self.trailerId:
			self.session.open(
				YoutubePlayer,
				[(self.filmName+' - Trailer', self.trailerId, self.imageUrl)],
				playAll = False,
				showPlaylist=False,
				showCover=True
				)

	def keyOK(self):
		if self.keyLocked:
			return
		url = self['liste'].getCurrent()[0][1]
		if not url.startswith('http'):
			url = BASE_URL + url
		data = sit_grabpage(url)
		self.getUrl(data)

	def getUrl(self,data):
		try:
			link = re.search('id="download" class="cd" style="display:none"><a href="(.*?)">', data).group(1)
			us = urlparse.urlsplit(link)
			link = urlparse.urlunsplit(us[0:1]+(us[1].lower(),)+us[2:])
		except:
			link = "http://fuck.com"
		get_stream_link(self.session).check_link(link, self.gotLink)