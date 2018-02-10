# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.twagenthelper import TwAgentHelper
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
import base64

class PrimeWireGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['ContentTitle'] = Label("Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.primewire.ag/"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="opener-menu-genre">(.*)class="opener-menu-section', data, re.S)
		Cats = re.findall('<a\shref="(.*?)">(.*?)</a>', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = "http://www.primewire.ag" + Url + "&page="
				self.genreliste.append((Title, Url))
			self.genreliste.sort()
			self.genreliste.insert(0, ("--- Search ---", "callSuchen"))
			self.genreliste.insert(1, ("Featured Movies", "http://www.primewire.ag/index.php?sort=featured&page="))
			self.genreliste.insert(2, ("Popular Movies", "http://www.primewire.ag/index.php?sort=views&page="))
			self.genreliste.insert(3, ("Top Rated Movies", "http://www.primewire.ag/index.php?sort=ratings&page="))
			self.genreliste.insert(4, ("Newly Released Movies", "http://www.primewire.ag/index.php?sort=release&page="))
			self.genreliste.insert(5, ("TV Shows", ""))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.ml.moveToIndex(0)
			self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		if auswahl == "--- Search ---":
			self.suchen()
		elif auswahl == "TV Shows":
			self.session.open(PrimeWireTVshowsScreen)
		else:
			self.session.open(PrimeWireFilmlisteScreen, url, auswahl)

	def SuchenCallback(self, callback = None, entry = None):
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			auswahl = "--- Search ---"
			url = "http://www.primewire.ag/?search_keywords=%s&search_section=1&page=" % self.suchString
			self.session.open(PrimeWireFilmlisteScreen, url, auswahl)

class PrimeWireTVshowsScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['ContentTitle'] = Label("TV Shows Genre:")
		self.keyLocked = True
		self.suchString = ''

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		url = "http://www.primewire.ag/?tv"
		getPage(url).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('class="opener-menu-genre">(.*)class="opener-menu-section', data, re.S)
		Cats = re.findall('<a\shref="(.*?)">(.*?)</a>', parse.group(1), re.S)
		if Cats:
			for (Url, Title) in Cats:
				Url = "http://www.primewire.ag/?tv&genre=" + Url + "&page="
				self.genreliste.append((Title, Url))
		self.genreliste.sort()
		self.genreliste.insert(0, ("Popular TV Shows", "http://www.primewire.ag/?tv=&sort=views&page="))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		self.session.open(PrimeWireFilmlisteScreen, url, 'TV Shows %s' % auswahl )

class PrimeWireFilmlisteScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, Url, Genre):
		self.Url = Url
		self.Genre = Genre
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel" : self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"yellow" : self.keyFilter,
			"green" : self.keyPageNumber,
			"blue" : self.keySort
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['ContentTitle'] = Label("Genre: %s" % self.Genre)
		self['Page'] = Label(_("Page:"))
		self['F2'] = Label(_("Page"))
		self['F3'] = Label(_("Filter"))
		if not re.match(".*?Popular TV Shows|--- Search ---", self.Genre):
			self['F4'] = Label(_("Sort"))

		self.streamList = []
		self.handlung = ""
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.sort = None
		self.filter = None
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = "%s%s" % (self.Url, str(self.page))
		if self.sort:
			url = "%s&sort=%s" % (url, self.sort)
		if self.filter:
			url = "%s&country=%s" % (url, self.filter)
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.lastpage = re.findall('<div class="number_movies_result">(.*?)\sitems found</div>', data)
		if self.lastpage:
			self.lastpage = int(self.lastpage[0].replace(',',''))/24+1
		else:
			self.lastpage = 999
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		chMovies = re.findall('<div\sclass="index_item\sindex_item_ie">.*?<a\shref="(.*?)"\stitle="Watch.(.*?)"><img\ssrc="(.*?)"', data, re.S)
		if chMovies:
			for (chUrl,chTitle,chImage) in chMovies:
				chUrl = "http://www.primewire.ag" + chUrl
				chImage = "http:"+chImage
				self.streamList.append((decodeHtml(chTitle),chUrl,chImage))
		if len(self.streamList) == 0:
			self.streamList.append((_('No videos found!'), '', None))
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.keyLocked = False
		self.th_ThumbsQuery(self.streamList,0,1,2,None,None, self.page, self.lastpage)
		self.showInfos()

	def showInfos(self):
		self.image = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(self.image)
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=std_headers).addCallback(self.showInfos2).addErrback(self.dataError)

	def showInfos2(self, data):
		Handlung = re.search('display:block;">(.*?)</p></td>', data, re.S)
		if Handlung:
			self.handlung = Handlung.group(1).strip()
		else:
			self.handlung = ""
		self['handlung'].setText(decodeHtml(self.handlung))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		if re.match('TV Shows', self.Genre):
			self.session.open(PrimeWireEpisodeScreen, Link, Name)
		else:
			self.session.open(PrimeWireStreamsScreen, Link, Name, self.image, self.handlung)

	def keySort(self):
		if self.keyLocked or re.match(".*?Popular TV Shows|--- Search ---", self.Genre):
			return
		rangelist = [ ['Alphabet', 'alphabet'], ['Data Added', 'date'], ['Popular', 'views'], ['Ratings','ratings'], ['Favorites','favorites'], ['Release Date', 'release'],['Featured','featured']]
		self.session.openWithCallback(self.keySortAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keySortAction(self, result):
		if result:
			self['F4'].setText(result[0])
			self.sort = result[1]
			self.page = 1
			self.loadPage()

	def keyFilter(self):
		if self.keyLocked:
			return
		rangelist = [ ['All', ''], ['Germany', 'Germany'], ['USA', 'USA'], ['UK', 'UK'], ['Netherlands','Netherlands'], ['Austria','Austria'], ['Greece','Greece'], ['Russia','Russia'], ['Spain', 'Spain'], ['Turkey','Turkey']]
		self.session.openWithCallback(self.keyFilterAction, ChoiceBoxExt, title=_('Select Action'), list = rangelist)

	def keyFilterAction(self, result):
		if result:
			self['F3'].setText(result[0])
			self.filter = result[1]
			self.page = 1
			self.loadPage()

class PrimeWireEpisodeScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['ContentTitle'] = Label("Episoden: %s" % self.Name)

		self.streamList = []
		self.handlung = ""
		self.image = None
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.Link).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		parse = re.search('class="choose_tabs">(.*?)class="download_link">', data, re.S)
		if parse:
			episoden = re.findall('class="tv_episode_item.*?">.*?<a\shref="(.*?)">.*?episode_name">\s{0,2}-\s{0,2}(.*?)</span', parse.group(1), re.S|re.I)
		if episoden:
			for (url,title) in episoden:
				episodes = re.findall('season-(.*?)-episode-(.*?)$', url, re.S)
				if int(episodes[0][0]) < 10:
					season = "S0"+str(episodes[0][0])
				else:
					season = "S"+str(episodes[0][0])
				if int(episodes[0][1]) < 10:
					episode = "E0"+str(episodes[0][1])
				else:
					episode = "E"+str(episodes[0][1])
				Title = "%s%s - %s" % (season, episode, title)
				url = "http://www.primewire.ag" + url
				self.streamList.append((decodeHtml(Title),url))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.keyLocked = False
			self.showInfos()

	def showInfos(self):
		url = self['liste'].getCurrent()[0][1]
		getPage(url, agent=std_headers).addCallback(self.showInfos2).addErrback(self.dataError)

	def showInfos2(self, data):
		Image = re.search('og:image"\scontent="(.*?)"', data, re.S)
		Handlung = re.search('display:block;">(.*?)</p></td>', data, re.S)
		if Handlung:
			self.handlung = Handlung.group(1).strip()
		else:
			self.handlung = ""
		if Image:
			self.image = Image.group(1)
		else:
			self.image = None
		self['handlung'].setText(decodeHtml(self.handlung))
		CoverHelper(self['coverArt']).getCover(self.image)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(PrimeWireStreamsScreen, Link, Name, self.image, self.handlung)

class PrimeWireStreamsScreen(MPScreen):

	def __init__(self, session, Link, Name, Image, Handlung):
		self.Link = Link
		self.Name = Name
		self.image = Image
		self.handlung = Handlung
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0": self.closeAll,
			"cancel": self.keyCancel,
		}, -1)

		self['title'] = Label("PrimeWire.ag")
		self['ContentTitle'] = Label("Streams: %s" % self.Name)

		self.tw_agent_hlp = TwAgentHelper()
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		getPage(self.Link).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		isSerie = re.search('<div class="tv_container">', data, re.S)
		if isSerie:
			self.session.open(PrimeWireEpisodeScreen, self.Link, self.Name)
			self.close()
		streams = re.findall('<a href="/gohere.php\?title=.*?&url=(.*?)&domain=.*?document.writeln\(\'([^<].*?)\'\)', data, re.S)
		if streams:
			for (Url, StreamHoster) in streams:
				if isSupportedHoster(StreamHoster, True):
					self.streamList.append((StreamHoster, Url))
			if len(self.streamList) == 0:
				self.streamList.append((_('No supported streams found!'), None))
			else:
				self.keyLocked = False
		else:
			self.streamList.append((_('No supported streams found!'), None))
		self.ml.setList(map(self._defaultlisthoster, self.streamList))
		self['handlung'].setText(self.handlung)
		CoverHelper(self['coverArt']).getCover(self.image)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		url = self['liste'].getCurrent()[0][1]
		url = base64.b64decode(url)
		get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.Name, stream_url, self.image)], showPlaylist=False, ltype='primewire', cover=True)