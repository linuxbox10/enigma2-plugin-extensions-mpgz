# -*- coding: utf-8 -*-
import Queue
import threading
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper

DDLME_Version = "ddl.me"

class show_DDLME_Genre(MenuHelper):

	def __init__(self, session):
		genreBase = ["/search_99/?q=", "/moviez_", "/episodez_", "/abookz_", "", "", "", "", "", "", ""]

		genreMenu = [
			[
			("Suche...", ""),
			("Filme", ""),
			("Serien", "")
			],
			[None,
			[
			("Neue Filme", "/update_0_1"),
			("Neue Blockbuster", "/update_0_1"),
			("Alle", "00_%d_1_%d"),
			("Kinofilme", "23_%d_1_%d"),
			("Abenteuer", "01_%d_1_%d"),
			("Action", "02_%d_1_%d"),
			("Animation", "03_%d_1_%d"),
			("Biografie", "04_%d_1_%d"),
			("Blockbuster", "25_%d_1_%d"),
			("Doku", "06_%d_1_%d"),
			("Drama", "07_%d_1_%d"),
			("Familie", "08_%d_1_%d"),
			("Fantasie", "09_%d_1_%d"),
			("Geschichte", "10_%d_1_%d"),
			("Horror", "11_%d_1_%d"),
			("Klassiker", "12_%d_1_%d"),
			("Komödie", "13_%d_1_%d"),
			("Kriegsfilm", "14_%d_1_%d"),
			("Musik", "15_%d_1_%d"),
			("Mystery", "16_%d_1_%d"),
			("Romantisch", "17_%d_1_%d"),
			("SciFi", "18_%d_1_%d"),
			("Sport", "20_%d_1_%d"),
			("Thriller", "21_%d_1_%d"),
			("Western", "22_%d_1_%d")
			],
			[
			("Neue Serien", "/update_0_1"),
			("Alle", "00_%d_1_%d"),
			("Abenteuer", "01_%d_1_%d"),
			("Action", "02_%d_1_%d"),
			("Animation", "03_%d_1_%d"),
			("Doku", "06_%d_1_%d"),
			("Drama", "07_%d_1_%d"),
			("Familie", "08_%d_1_%d"),
			("Fantasie", "09_%d_1_%d"),
			("Geschichte", "10_%d_1_%d"),
			("Horror", "11_%d_1_%d"),
			("Komödie", "13_%d_1_%d"),
			("Mystery", "16_%d_1_%d"),
			("Romantisch", "17_%d_1_%d"),
			("SciFi", "18_%d_1_%d"),
			("Sport", "20_%d_1_%d"),
			("Thriller", "21_%d_1_%d"),
			("Western", "22_%d_1_%d")
			],
			[
			("Alle", "00_%d_1_%d"),
			("Thriller", "01_%d_1_%d"),
			("Krimi", "02_%d_1_%d"),
			("Fantasy", "03_%d_1_%d"),
			("Horror", "04_%d_1_%d"),
			("SciFi", "05_%d_1_%d"),
			("Romane", "06_%d_1_%d"),
			("Historisch", "07_%d_1_%d"),
			("Klassiker", "08_%d_1_%d"),
			("Humor", "09_%d_1_%d"),
			("Bildung & Wissen", "10_%d_1_%d"),
			("Freizeit & Leben", "11_%d_1_%d"),
			("Karriere", "12_%d_1_%d"),
			("Kinder", "13_%d_1_%d"),
			("Jugendliche", "14_%d_1_%d"),
			("Erotik", "15_%d_1_%d")
			]
			],
			[
			None, None, None, None
			]
			]

		MenuHelper.__init__(self, session, 1, genreMenu, "http://de.ddl.me", genreBase, self._defaultlistcenter)

		self['title'] = Label(DDLME_Version)
		self['ContentTitle'] = Label("Genres")

		self.param_qr = ''

		self.onLayoutFinish.append(self.mh_loadMenu)

	def mh_callGenreListScreen(self):
		if re.search('Suche...', self.mh_genreTitle):
			self.paraQuery()
		else:
			if re.search('Neue (Filme|Serien|Blockbuster)', self.mh_genreTitle):
				genreurl = self.mh_baseUrl+self.mh_genreUrl[0]+self.mh_genreUrl[1]
			else:
				genreurl = self.mh_baseUrl+self.mh_genreBase[self.mh_menuIdx[0]]+self.mh_genreUrl[0]+self.mh_genreUrl[1]
			self.session.open(DDLME_FilmListeScreen, genreurl, self.mh_genreTitle)

	def paraQuery(self):
		self.param_qr = ''
		self.session.openWithCallback(self.cb_paraQuery, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = self.param_qr, is_dialog=True, auto_text_init=True)

	def cb_paraQuery(self, callback = None, entry = None):
		if callback != None:
			self.param_qr = callback.strip()
			if len(self.param_qr) > 0:
				qr = urllib.quote_plus(self.param_qr)
				genreurl = self.mh_baseUrl+self.mh_genreBase[self.mh_menuIdx[0]]+qr
				self.session.open(DDLME_FilmListeScreen, genreurl, self.mh_genreTitle)

class DDLME_FilmListeScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, genreLink, genreName, imgLink=None):
		self.genreLink = genreLink
		self.genreName = genreName
		self.imgLink = imgLink
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
			"0" : self.closeAll,
			"yellow" :  self.keyYellow
		}, -1)

		self.sortOrderTxt = ['Letztem Update', 'Blockbuster', 'IMDb Rating', 'Jahr']
		self.baseUrl = "http://de.ddl.me"
		self.genreTitle = ""
		self['title'] = Label(DDLME_Version)
		self['F3'] = Label(_("Sorting"))
		self['Page'] = Label(_("Page:"))


		self.timerStart = False
		self.seekTimerRun = False
		self.filmQ = Queue.Queue(0)
		self.eventL = threading.Event()
		self.keyLocked = True
		self.filmListe = []
		self.page = 0
		self.pages = 0;
		self.serienEpisoden = re.search('Episoden -', self.genreName)
		self.genreFilme = re.search('Filme', self.genreName)
		self.genreSerien = re.search('Serien', self.genreName)
		self.genreABook = re.search('Hörbücher', self.genreName)
		self.genreSearch = re.search('Suche...', self.genreName)
		self.genreUpdates = re.search('Neue (Filme|Serien|Blockbuster)', self.genreName)
		self.genreSpecials = self.serienEpisoden or self.genreSearch or self.genreUpdates

		self.setGenreStrTitle()

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def setGenreStrTitle(self):
		if self.genreSpecials:
			genreName = "%s%s" % (self.genreTitle,self.genreName)
			self['F3'].hide()
		else:
			self['F3'].show()
			genreName = "%s%s - Sortierung: %s" % (self.genreTitle,self.genreName,self.sortOrderTxt[mp_globals.ddlme_sortOrder])
		self['ContentTitle'].setText(genreName)

	def loadPage(self):
		if self.genreSpecials:
			url = self.genreLink
		else:
			page = self.page
			if page < 1:
				page = 1
			url = self.genreLink % (mp_globals.ddlme_sortOrder, page)

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
		twAgentGetPage(url, agent=None, headers=std_headers).addCallback(self.loadPageData).addErrback(self.dataError)

	def dataError(self, error):
		self.eventL.clear()
		printl(error,self,"E")
		self['handlung'].setText("Fehler:\n" + str(error))

	def loadPageData(self, data):
		self.filmListe = []

		if self.serienEpisoden:
			info = re.search('var subcats =.*?"info":', data)
			if info:
				self.pages = 1
				self.page = 1
				a = info.start()
				l = len(data)
				h = self.genreLink
				while a<l:
					info = re.search('"info":.*?"name":"(.*?)".*?"nr":"(.*?)".*?"staffel":"(.*?)"', data[a:])
					if info:
						a += info.end()
						nm = decodeHtml(info.group(1))
						i = nm.find('\u')
						if i>0:
							nm = nm[:i]

						t = 'S%02dE%02d - %s' % (int(info.group(3)), int(info.group(2)), nm)
						self.filmListe.append((t, h, self.imgLink, '', ''))
					else:
						a = l
		elif self.genreUpdates:
			m = None
			if 'Neue Filme' in self.genreName:
				m = re.search(">Neue Filme<.*?<div id='view' class='small one'>(.*?)</div><div class=.hr.", data)
			elif 'Neue Serien' in self.genreName:
				m = re.search(">Neue Serien<.*?<div id='view' class='small one'>(.*?)</div><div class=.hr.", data)
			elif 'Neue Blockbuster' in self.genreName:
				m = re.search(">Neue Blockbuster<.*?<div id='view' class='small one'>(.*?)</div><div class=.hr.", data)

			if m:
				m = re.findall('title=\'(.*?)\'.*?href=\'(.*?)\'.*?<img.*?(http[s]?://.*?jpg)', m.group(1))
				if m:
					self.page = 1
					self.pages = 1
					for (t, h, i) in m:
						self.filmListe.append((decodeHtml(t), "%s%s" % (self.baseUrl, h), i, '', ''))
		else:
			if self.genreSearch:
				mg = re.search("<div id='view'(.*?)class=\"clear\">", data)
				if not 'class="heading"' in data:
					mg = None
			else:
				mg = re.search("<div id='view'(.*?)class='clear'>", data)

			if mg:
				if self.genreSearch:
					m = re.findall('title=\'(.*?)\'.*?href=\'(.*?)\'.*?<img.*?src=\'(.*?)\'.*?(>TV<|>Film<)/span>.*?class=\'stars\'.*?rel=\'(.*?)\'', mg.group(1))
				else:
					m = re.findall('title=\'(.*?)\'.*?href=\'(.*?)\'.*?<img.*?src=\'(.*?)\'.*?class=\'stars\'.*?rel=\'(.*?)\'', mg.group(1))
				if m:

					if self.genreSearch:
						for (t, h, i, sm, r) in m:
							imdb = 'IMDb: %s / 10' % r
							self.filmListe.append((decodeHtml(t), "%s%s" % (self.baseUrl, h), i, sm, ''))
					else:
						for (t, h, i, r) in m:
							imdb = 'IMDb: %s / 10' % r
							self.filmListe.append((decodeHtml(t), "%s%s" % (self.baseUrl, h), i, '', imdb))

				if not self.pages:
					m1 = re.search('Seite.*?von(.*?)</h1>', data)

					if m1:
						pages = int(m1.group(1))
					else:
						pages = 1

					if pages > 999:
						self.pages = 999
					else:
						self.pages = pages

					self.page = 1
		self['page'].setText("%d / %d" % (self.page,self.pages))

		if len(self.filmListe) == 0:
			self.pages = 0
			self.filmListe.append((_('No movies/shows found!'),'','','',''))
		else:
			menu_len = len(self.filmListe)

		self.ml.setList(map(self.DDLME_FilmListEntry, self.filmListe))
		self.th_ThumbsQuery(self.filmListe, 0, 1, 2, None, None, self.page, self.pages)
		self.showInfos()

	def showInfos(self):
		streamName = self['liste'].getCurrent()[0][0]
		self['name'].setText(streamName)
		desc = None
		self.getHandlung(desc)

		if not self.filmQ.empty():
			self.loadPageQueued()
		else:
			self.eventL.clear()
		self.keyLocked	= False

		url = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(url)

	def getHandlung(self, desc):
		if desc == None:
			self['handlung'].setText(_("No further information available!"))
			return
		self.setHandlung(desc)

	def setHandlung(self, data):
		self['handlung'].setText(decodeHtml(data))

	def keyOK(self):
		if (self.keyLocked|self.eventL.is_set()):
			return
		url = self['liste'].getCurrent()[0][1]
		if not url:
			return
		title = self['liste'].getCurrent()[0][0]
		img = self['liste'].getCurrent()[0][2]
		sm = self['liste'].getCurrent()[0][3]
		genreSerien = self.genreSerien or sm == '>TV<' or re.search('Neue Serien', self.genreName)

		if not genreSerien:
			self.session.open(DDLMEStreams, url, title, img)
		else:
			self.session.open(DDLME_FilmListeScreen, url, 'Episoden - ' + title, imgLink=img)

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
		self.showInfos()

	def keyLeftRepeated(self):
		if self.keyLocked:
			return
		self['liste'].pageUp()

	def keyRightRepeated(self):
		if self.keyLocked:
			return
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

	def keyYellow(self):
		if not (self.keyLocked or self.genreSpecials):
			self.keyLocked = True
			mp_globals.ddlme_sortOrder += 1
			if mp_globals.ddlme_sortOrder > 3:
				mp_globals.ddlme_sortOrder = 0
			self.setGenreStrTitle()
			self.loadPage()

class DDLMEStreams(MPScreen):

	def __init__(self, session, filmUrl, filmName, imageLink):
		self.filmUrl = filmUrl
		self.filmName = filmName
		self.imageUrl = imageLink

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"green" 	: self.keyTrailer,
			"ok"    	: self.keyOK,
			"0"		: self.closeAll,
			"cancel"	: self.keyCancel
		}, -1)

		self['title'] = Label(DDLME_Version)
		self['ContentTitle'] = Label("Streams")

		self['name'] = Label(filmName)

		self.trailerId = None
		self.streamListe = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		streamUrl = self.filmUrl
		twAgentGetPage(streamUrl).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		mdesc = re.search('class=\'detailCover\'.*?>(.*?)<br><br>', data, re.S)
		if mdesc:
			desc = mdesc.group(1).strip()
			desc = stripAllTags(decodeHtml(desc))
		else:
			desc = _("No further information available!")

		m = re.search('http[s]?://www.youtube.com/watch\?v=(.*?)\'', data)
		if m:
			self.trailerId = m.group(1)
			self['F2'].setText('Trailer')

		self.streamListe = []
		info = re.search('var subcats =.*?"info":', data)
		if info:
			a = info.start()
			l = len(data)
			epi = re.search('S(\d{2})E(\d{2})', self.filmName)
			if epi:
				st = int(epi.group(1))
				ep = int(epi.group(2))
				while a<l:
					info = re.search('"info":.*?"nr":"(\d+)".*?"staffel":"(\d+)".*?links":{(.*?)}}', data[a:])
					if info:
						a += info.end()
						st_ = int(info.group(2))
						ep_ = int(info.group(1))
						if st == st_ and ep == ep_:
							a2=0
							l2=len(info.group(3))
							while a2<l2:
								mg = re.search('"(.*?)":\[(\[.*?\])\]', info.group(3)[a2:])
								if mg:
									a2 += mg.end()
									streams = re.findall('"(http[s]?:.*?)".*?("stream"|"download").*?\]', mg.group(2))

									if streams:
										s = mg.group(1)
										if isSupportedHoster(s, True):

											for h, t in streams:
												url = h.replace('\\', '')
												self.streamListe.append((s,url,'',''))
								else:
									a2 = l2
							a = l
					else:
						a = l
			self.ml.setList(map(self.DDLMEStreamListEntry, self.streamListe))
		else:
			np = re.search('var subcats =', data)
			if np:
				k = np.end()
				kl = len(data)
			else:
				k = kl = 0

			while k < kl:
				np = re.search('{"0":"(.*?)","1":"(\d)"', data[k:])
				if np:
					k += np.end()
					kap = np.group(1)
					n = int(np.group(2))
				else:
					k = kl
					continue

				ls = re.search('"links":{(.*?)}}', data)
				if ls:
					links = ls.group(1)
					l=len(links)
				else:
					continue

				a=0
				while a<l:
					mg = re.search('"(.*?)":\[(\[.*?\])\]', links[a:])
					if mg:
						a += mg.end()

						streams = re.findall('\["(.*?)".*?"(http[s]?:.*?)".*?("stream"|"download").*?\]', mg.group(2))

						if streams:
							s = mg.group(1)
							if isSupportedHoster(s, True):
								part = ''
								for (p, h, t) in streams:
									url = h.replace('\\', '')
									if n > 1:
										part = "Part " + p
									else:
										part = "One Part"
									self.streamListe.append((s,url,part,kap))
					else:
						a = l

			self.ml.setList(map(self.DDLMEStreamListEntry2, self.streamListe))
		if len(self.streamListe) == 0:
			self.streamListe.append((_("No supported streams found!"),"","",""))
			self.ml.setList(map(self._defaultlistleft, self.streamListe))

		self['handlung'].setText(decodeHtml(desc))
		self.keyLocked = False
		CoverHelper(self['coverArt']).getCover(self.imageUrl)

	def _insert(self, ori, ins, pos):
		return ori[:pos] + ins + ori[pos:]

	def dataError(self, error):
		printl(error,self,"E")
		self.streamListe.append(("Read error!","","",""))
		self.ml.setList(map(self.DDLMEStreamListEntry, self.streamListe))

	def got_link(self, stream_url):
		if not re.match('One', self['liste'].getCurrent()[0][2]):
			title = self.filmName + ' - ' + self['liste'].getCurrent()[0][2]
		else:
			title = self.filmName
		self.session.open(SimplePlayer, [(title, stream_url, self.imageUrl)], showPlaylist=False, ltype='ddl.me', cover=True)

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
		if streamLink:
			get_stream_link(self.session).check_link(streamLink, self.got_link)