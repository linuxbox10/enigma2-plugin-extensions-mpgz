# -*- coding: utf-8 -*-
#
#    Copyright (c) 2016 Billy2011, MediaPortal Team
#
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

SKTO_Version = "OnlineFilme.to"
SKTO_siteEncoding = 'utf-8'
BASE_URL = "http://onlinefilme.to"
BASE_URL2 = "http://onlinefilme.biz"
glob_cookies = CookieJar()

class show_SKTO_Genre(MenuHelper):

	def __init__(self, session):
		MenuHelper.__init__(self, session, 0, None, BASE_URL, "", self._defaultlistcenter, cookieJar=glob_cookies)

		self['title'] = Label(SKTO_Version)
		self['ContentTitle'] = Label("Genres")
		self.param_qr = ''
		self.search_token = None

		self.onLayoutFinish.append(self.mh_initMenu)

	def mh_parseCategorys(self, data):
		menu = []
		for m in re.finditer('<h2>(.*?)</h2>', data):
			menu.append((0, '', m.group(1)))

		m = re.search('"fa fa-caret-square-o-right"></i> Filme</a>(.*?)</div>\s+</div>\s+</li>\s+</ul>\s+</li', data, re.S)
		if m:
			menu.append((0, '', 'Filme'))
			for me in re.finditer('href="%s(.*?)"><strong>(.*?)</strong></a' % BASE_URL, m.group(1)):
				u, n = me.groups()
				menu.append((1, u, n))

		m = re.search('"fa fa-play-circle-o"></i> Serie</a>(.*?)</div>\s+</div>\s+</li>\s+</ul>\s+</li', data, re.S)
		if m:
			menu.append((0, '', 'Serien'))
			for me in re.finditer('href="%s(.*?)"><strong>(.*?)</strong></a' % BASE_URL, m.group(1)):
				u, n = me.groups()
				menu.append((1, u, n))

		m = re.search('<form.*?action="%s(.*?)".*?<input name="_token".*?value="(.*?)">' % BASE_URL, data)
		if m:
			menu.append((0, m.group(1), 'Suche...'))
			self.search_token = m.group(2)

		self.mh_genMenu2(menu)

	def mh_callGenreListScreen(self):
		if re.search('Suche...', self.mh_genreTitle):
			self.paraQuery()
		else:
			genreurl = self.mh_baseUrl+self.mh_genreUrl[self.mh_menuLevel]
			self.session.open(SKTO_FilmListeScreen, self.mh_baseUrl, genreurl, self.mh_genreTitle)

	def paraQuery(self):
		self.param_qr = ''
		self.session.openWithCallback(self.cb_paraQuery, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = self.param_qr, is_dialog=True, auto_text_init=True,  suggest_func=self.getSuggestions)

	def cb_paraQuery(self, callback = None, entry = None):
		if callback != None:
			self.param_qr = callback.strip()
			if self.param_qr:
				search_form={
					'_token' : self.search_token,
					'search_term' : self.param_qr,
					'search_type' : '0',
					'search_where' : '0',
					'search_year_from' : '1900',
					'search_year_to' : str(datetime.datetime.now().year),
					'start_rating' : '1',
					'end_rating' : '10'
					}
				genreurl = self.mh_baseUrl+self.mh_genreUrl[self.mh_menuLevel]
				self.session.open(SKTO_FilmListeScreen, self.mh_baseUrl, genreurl, self.mh_genreTitle, searchForm=search_form)

	def getSuggestions(self, text, max_res):
		url = "http://onlinefilme.to/filter-search/%s" % quote(text)
		d = twAgentGetPage(url, agent=None, headers=std_headers, timeout=5)
		d.addCallback(self.gotSuggestions, max_res)
		d.addErrback(self.gotSuggestions, max_res, True)
		return d

	def gotSuggestions(self, suggestions, max_res, err=False):
		list = []
		if not err and suggestions:
			for m in re.finditer('="margin-bottom:-6px;">\s*(.+?)\s+</div', suggestions):
				list.append(decodeHtml(m.group(1).rstrip()))
				max_res -= 1
				if not max_res: break
		elif err:
			printl(str(suggestions),self,'E')
		return list

class SKTO_FilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreBaseURL, genreLink, genreName, searchForm=None):
		self.genreLink = genreLink
		self.genreName = genreName
		self.searchForm = searchForm

		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

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
			"0"	: self.closeAll,
			"yellow" : self.keySort
		}, -1)

		self.sortFuncs = None
		self.sortFuncsSel = -1
		self.sortOrderStrGenre = ""
		self.genreTitle = "Filme in Genre "

		self.searchMovies = searchForm != None
		self['title'] = Label(SKTO_Version)
		self['F3'] = Label(_("Sort by..."))
		self['Page'] = Label(_("Page:"))
		self['F3'].hide()

		self.filmQ = Queue.Queue(0)
		self.hanQ = Queue.Queue(0)
		self.picQ = Queue.Queue(0)
		self.updateP = 0
		self.eventL = threading.Event()
		self.eventP = threading.Event()
		self.keyLocked = True
		self.dokusListe = []
		self.page = 0
		self.pages = 0;
		self.newMovies = genreBaseURL == genreLink

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def setGenreStrTitle(self):
		if self.sortOrderStrGenre:
			sortOrder = ' (%s)' % self.sortOrderStrGenre
		else:
			sortOrder = ''

		self['ContentTitle'].setText("%s%s%s" % (self.genreTitle,self.genreName,sortOrder))

	def loadPage(self):
		if self.page:
			url = '%s?page=%d' % (self.genreLink, self.page)
		else:
			url = self.genreLink

		#if not 'let=' in self.genreLink and not self.searchMovies:
		#	url += '&%s' % self.sortOrderStr[mp_globals.skto_sortOrder][1]

		if self.page:
			self['page'].setText("%d / %d" % (self.page,self.pages))
		self.filmQ.put(url)
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued()

	def loadPageQueued(self):
		self['name'].setText(_('Please wait...'))
		while not self.filmQ.empty():
			url = self.filmQ.get_nowait()
		if not self.searchMovies:
			twAgentGetPage(url).addCallback(self.loadPageData).addErrback(self.dataError)
		else:
			twAgentGetPage(url, method='POST', cookieJar=glob_cookies, postdata=urlencode(self.searchForm), headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		self.eventL.clear()
		printl(error,self,"E")
		self.dokusListe.append((_("No movies / series found!"),"","","",""))
		self.ml.setList(map(self.DDLME_FilmListEntry, self.dokusListe))

	def loadPageData(self, data):
		self.getPostFuncs(data)
		self.dokusListe = []
		if self.newMovies:
			m = re.search('<h2>%s</h2>(.*?)</ul>\s+</div>\s+</div>' % self.genreName, data, re.S)
		elif self.searchMovies:
			m = re.search('<h1>Ihr Suchwort:(.*?)</div>\s*</a>\s+</li>\s+</ul>', data, re.S)
		else:
			m = re.search('id="listing-top-holder">(.*?)</ul>\s+</div>\s+</div>', data, re.S)
		if m:
			for me in re.finditer('href="(.*?)".+?<img.*?="(.*?)".*?title="(.*?)".*?\((\d+)\)(.*?)</strong>.*?Views:\s(\d+).*?Länge:\s(.*?\s\w+)\s.*?IMDB rating:\s(.*?)\s.*?Uploaded:\s(.*?)\s', m.group(1), re.S):
				url, img, name, year, staffel, views, laenge, imdb, uploaded = me.groups()
				staffel = staffel.replace(' : ','').strip()
				infos = (year, views, laenge.replace('min', ' Min.'), imdb, uploaded, staffel.title())
				imdb = 'IMDb: %s / 10' % imdb
				name = decodeHtml(name.strip())
				name = re.sub('\s+', ' ', name)

				if staffel and name.endswith(staffel):
					name = name.split(':')[0].strip()
					name += ' - ' + infos[5]
				elif staffel:
					name += ' - ' + infos[5]

				self.dokusListe.append((name, url, BASE_URL+img, infos, imdb))

			if not self.pages:
				ps = re.findall('href=\".*?page=.*?\">(\d+)</a>', data)
				try:
					pages = int(ps[-1])
				except:
					pages = 1
				self.pages = min(pages,999)
			if not self.page:
				self.page = 1

		if len(self.dokusListe):
			self['page'].setText("%d / %d" % (self.page,self.pages))
			self.ml.setList(map(self.DDLME_FilmListEntry, self.dokusListe))
			self.th_ThumbsQuery(self.dokusListe, 0, 1, 2, None, None, self.page, self.pages)
			self.loadPicQueued()
		else:
			self.dokusListe.append((_("No movies / series found!"),"","","",""))
			self.ml.setList(map(self.DDLME_FilmListEntry, self.dokusListe))
			if self.filmQ.empty():
				self.eventL.clear()
			else:
				self.loadPageQueued()

	def getPostFuncs(self, data):
		self.sortFuncs = []
		m = re.search('<dl class="sub-nav">\s+<dt>\s+Reihenfolge:\s+</dt>(.*?)</dl>', data, re.S)
		if m:
			i = 0
			for m2 in re.finditer('<dd class="(.*?)">\s+<a href="(.*?)">(.*?)</a', m.group(1)):
				active, href, name = m2.groups()
				name = decodeHtml(name)
				if active == 'active' and self.sortFuncsSel != i:
					self.sortFuncsSel = i
					self.sortOrderStrGenre = name
					self.setGenreStrTitle()
				self.sortFuncs.append((name, (decodeHtml(href), i)))
				i += 1
		if self.sortFuncs:
			self['F3'].show()
		else:
			self['F3'].hide()

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

	def showInfos(self):
		infos = self['liste'].getCurrent()[0][3]
		text = 'Jahr:\t%s\nViews:\t%s\nLänge:\t%s\nIMDb:\t%s\nUploaded:\t%s' % (infos[0], infos[1], infos[2], infos[3], infos[4])
		self['handlung'].setText(text)

	def ShowCoverFileExit(self):
		self.updateP = 0;
		self.keyLocked	= False
		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
			self.loadPic()

	def loadPicQueued(self):
		self.picQ.put(None)
		if not self.eventP.is_set():
			self.eventP.set()
		self.loadPic()

	def keyOK(self):
		if (self.keyLocked|self.eventL.is_set()):
			return

		streamLink = self['liste'].getCurrent()[0][1]
		streamName = self['liste'].getCurrent()[0][0]
		imageLink = self['liste'].getCurrent()[0][2]
		infos = self['liste'].getCurrent()[0][3]
		self.session.open(SKTO_Streams, streamLink, streamName, imageLink, infos)

	def keyUpRepeated(self):
		if self.keyLocked:
			return
		self['liste'].up()

	def keyDownRepeated(self):
		if self.keyLocked:
			return
		self['liste'].down()

	def key_repeatedUp(self):
		if self.keyLocked:
			return
		self.loadPicQueued()

	def keyLeftRepeated(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()

	def keyRightRepeated(self):
		if self.keyLocked:
			return
		self['liste'].pageDown()

	def keyPageDown(self):
		self.keyPageDownFast(1)

	def keyPageUp(self):
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
		if self.keyLocked or 'let=' in self.genreLink or self.searchMovies:
			return
		if mp_globals.skto_sortOrder < (len(self.sortOrderStr) - 1):
			mp_globals.skto_sortOrder += 1
		else:
			mp_globals.skto_sortOrder = 0
		self.setGenreStrTitle()
		self.loadPage()

	def keySort(self):
		if not self.keyLocked and self.sortFuncs:
			self.handleSort()

	def handleSort(self):
		self.session.openWithCallback(self.cb_handleSort, ChoiceBoxExt, title=_("Sort Selection"), list = self.sortFuncs, selection=self.sortFuncsSel)

	def cb_handleSort(self, answer):
		href = answer and answer[1][0]
		if href:
			self.sortFuncsSel = answer[1][1]
			self.genreLink = href
			self.sortOrderStrGenre = answer[0]
			self.setGenreStrTitle()
			self.loadPage()

class SKTO_Streams(MPScreen):
	baseUrl = 'http://onlinefilme.to/'

	def __init__(self, session, filmUrl, filmName, imageLink, infos):
		self.filmUrl = filmUrl
		self.filmName = filmName
		self.imageUrl = imageLink
		self.infos = infos

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"green" 	: self.keyTrailer,
			"ok"    	: self.keyOK,
			"0"		: self.closeAll,
			"cancel"	: self.keyCancel
		}, -1)

		self['title'] = Label(SKTO_Version)
		self['ContentTitle'] = Label(_("Stream Selection")+': '+filmName)


		self.trailerId = None
		self.cookies = CookieJar()
		self.headers = {'Referer':BASE_URL, 'User-Agent':'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0'}
		self.streamListe = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_('Please wait...'))
		streamUrl = self.filmUrl
		twAgentGetPage(streamUrl, cookieJar=glob_cookies).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self['name'].setText(self.filmName)

		infos = 'Länge:\t%s\t' % self.infos[2]

		m = re.search('<h2>Voice over:</h2>(.*?)</',data, re.S)
		if m:
			infos += 'Sprache:\t%s' % m.group(1).strip()
		else:
			infos += 'Sprache:\tN/A'

		infos += '\nIMDb:\t%s\t' % self.infos[3]

		infos += 'Views:\t%s\n' % self.infos[1]

		infos += 'Uploaded:\t%s\n' % self.infos[4]

		m = re.search('\s{60}<p>(.*?)</p>',data,re.S)
		if m:
			infos += decodeHtml(m.group(1).strip())

		m = re.search('//.*?youtube\.com/(embed|v|p)/(.*?)(\?|" |&amp)', data)
		if m:
			self.trailerId = m.group(2)
			self['F2'].setText('Trailer')

		self.streamListe = []
		if not 'href="#panel' in data:
			for m in re.finditer('<div class="row">(.*?)</div>\s+</div>\s+</div>', data, re.S):
				m2 = re.search('<span data-tooltip aria-haspopup="true" title="(.*?)"', m.group(1))
				if not m2: continue
				hoster = m2.group(1)
				m2 = re.search('<a href=.(http.*?).\s.*?>Weiter</a>', m.group(1))
				if not m2: continue
				url = m2.group(1)
				if isSupportedHoster(hoster, True):
					self.streamListe.append((hoster,url,''))
		else:
			for m in re.finditer('<a href="#panel(.*?)">(.*?</div>\s+</div>\s+</div>)\s+<br>', data, re.S):
				for m2 in re.finditer('<div class="row">(.*?)</div>\s+</div>\s+</div>', m.group(2), re.S):
					m3 = re.search('<span data-tooltip aria-haspopup="true" title="(.*?)"', m2.group(1))
					if not m3: continue
					hoster = m3.group(1)
					m3 = re.search('<a href=.(http.*?).\s.*?>Weiter</a>', m2.group(1))
					if not m3: continue
					url = m3.group(1)
					if isSupportedHoster(hoster, True):
						ep = ' - Episode %s' % m.group(1)
						self.streamListe.append((hoster+ep,url,ep))

		if self.streamListe:
			self.keyLocked = False
		else:
			self.streamListe.append(("No streams found!","",""))

		self.ml.setList(map(self._defaultlisthoster, self.streamListe))
		self['handlung'].setText(infos)
		CoverHelper(self['coverArt']).getCover(self.imageUrl)

	def dataError(self, error):
		printl(error,self,"E")
		self.streamListe.append(("Read error !",""))
		self.ml.setList(map(self._defaultlisthoster, self.streamListe))

	def got_link(self, stream_url):
		if not stream_url:
			message = self.session.open(MessageBoxExt, _("No supported streams found!"), MessageBoxExt.TYPE_INFO, timeout=3)
		else:
			title = self.filmName + self['liste'].getCurrent()[0][2]
			self.session.open(SimplePlayer, [(title, stream_url, self.imageUrl)], cover=True, showPlaylist=False, ltype='onlinefilme')

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
		streamLink = self['liste'].getCurrent()[0][1]
		twAgentGetPage(streamLink, cookieJar=glob_cookies).addCallback(self.getLinkData).addErrback(self.streamError)

	def getLinkData(self, data):
		hoster = self['liste'].getCurrent()[0][0].replace(".", " ").split(" ")[0]
		parse = re.search('title="%s.*?href="(watch.*?)"' % hoster, data, re.S|re.I)
		if parse:
			url = BASE_URL2 + "/" + parse.group(1)
			twAgentGetPage(url, cookieJar=glob_cookies, addlocation=True, followRedirect=True).addCallback(self.getLink).addErrback(self.streamError)
		else:
			self.got_link(None)

	def getLink(self, result):
		data, location = result
		if location and not BASE_URL in location and not BASE_URL2 in location:
			streamLink = location
		else:
			streamLink = None
			if '<div><iframe src="' in data:
				m = re.search('<div><iframe src="(.*?)"', data)
				if m:
					streamLink = m.group(1).split('&')[0]
			elif 'class="flex-video">' in data:
				m = re.search('class="flex-video">\s+<iframe.*?src="(.*?)"', data)
				if m:
					streamLink = m.group(1).split('&')[0]

		if streamLink and not BASE_URL in streamLink and not BASE_URL2 in streamLink:
			get_stream_link(self.session).check_link(streamLink, self.got_link)
		else:
			self.got_link(None)

	def streamError(self, error):
		printl(error,self,"E")
		self.got_link(None)