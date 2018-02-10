# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
import base64

class gAnimeMain(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Genx-Anime.org")
		self['ContentTitle'] = Label(_("Genre Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("A-Z (Komplettliste)", "all"))
		self.streamList.append(("0-9", "num"))
		for c in xrange(26):
			self.streamList.append((chr(ord('A') + c), chr(ord('A') + c)))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][0]
		url = 'http://www.genx-anime.org/index.php?do=display&order=original&char=' + self['liste'].getCurrent()[0][1] + '&page='
		self.session.open(gAnimeParsing, auswahl, url)

class gAnimeParsing(MPScreen, ThumbsHelper):

	def __init__(self, session, genre, url):
		self.genre = genre
		self.url = url
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"5" : self.keyShowThumb,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("Genx-Anime.org")
		self['ContentTitle'] = Label("%s" % self.genre)

		self['Page'] = Label(_("Page:"))

		self.page = 1
		self.lastpage = 1
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		url = self.url+str(self.page)
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, 'corner_bot">(.*?)</dt>', '.*page=(\d+)')
		movies = re.findall('<a href="(index.php\?do=display&title=.*?)."><span class="genre_hint" title="(.*?)<img class=\'vorschaubild\' src=\'(.*?)\'>', data, re.S)
		if movies:
			for (Url, Title, Image) in movies:
				Title = Title.replace('|','')
				Url = "http://www.genx-anime.org/" + Url
				Image = "http://www.genx-anime.org/" + Image
				self.streamList.append((decodeHtml(Title), Url, Image))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.ml.moveToIndex(0)
			self.keyLocked = False
			self.th_ThumbsQuery(self.streamList, 0, 1, 2, None, None, 1, 1)
			self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		self['name'].setText(filmName)
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		stream_name = self['liste'].getCurrent()[0][0]
		movie_url = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(gAnimeFolgen, stream_name, movie_url, cover)

class gAnimeFolgen(MPScreen):

	def __init__(self, session, stream_name, url, cover):
		self.stream_name = stream_name
		self.url = url
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Genx-Anime.org")
		self['ContentTitle'] = Label(_("Episode Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		getPage(self.url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.streamList = []
		folgen = re.findall('title:\'(.*?)\'.*?content:(.*?)height:', data, re.S)
		if folgen:
			for folge, streamRAW in folgen:
				streams = re.findall('href="index.php\?do=fwd&link=(.*?)">(.*?)</a>', streamRAW, re.S)
				if streams:
					self.streamList.append((folge, streams))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			CoverHelper(self['coverArt']).getCover(self.cover)
			self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		folge = self['liste'].getCurrent()[0][0]
		streams = self['liste'].getCurrent()[0][1]
		print folge, streams
		self.session.open(gAnimeStreams, folge, streams, self.cover)

class gAnimeStreams(MPScreen):

	def __init__(self, session, stream_name, streams, cover):
		self.stream_name = stream_name
		self.streams = streams
		self.cover = cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0": self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Genx-Anime.org")
		self['ContentTitle'] = Label(_("Stream Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		for streamCrypted, streamName in self.streams:
			if isSupportedHoster(streamName, True):
				streamName = streamName.replace('www.','')
				self.streamList.append((streamName, streamCrypted))
			self.ml.setList(map(self._defaultlisthoster, self.streamList))
			CoverHelper(self['coverArt']).getCover(self.cover)
			self.keyLocked = False

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		streamUrl = self['liste'].getCurrent()[0][1]
		streamUrl = base64.b64decode(streamUrl).replace('$0','')
		print streamUrl
		get_stream_link(self.session).check_link(streamUrl, self.playfile)

	def playfile(self, stream_url):
		if stream_url != None:
			self.session.open(SimplePlayer, [(self.stream_name, stream_url, self.cover)], showPlaylist=False, ltype='genxanime', cover=True)