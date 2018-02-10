# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

class nwanimeMain(MPScreen):
	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("NWANIME")
		self['ContentTitle'] = Label(_(_("Genre Selection")))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("Animes von A-Z", "animes"))
		self.streamList.append(("Watchlist", "watchlist"))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return

		auswahl = self['liste'].getCurrent()[0][1]
		if auswahl == "animes":
			self.session.open(nwanimeAnimes)
		else:
			self.session.open(nwanimeWatchlist)

class nwanimeAnimes(MPScreen, SearchHelper):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', widgets=('MP_widget_search',))
		SearchHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"green" : self.keyAdd,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("NWANIME")
		self['ContentTitle'] = Label("Animes von A-Z")
		self['F2'] = Label(_("Add to Watchlist"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def goToNumber(self, num):
		self.keyNumberGlobal(num, self.streamList)
		self.showSearchkey(num)

	def goToLetter(self, key):
		self.keyLetterGlobal(key, self.streamList)
		
	def loadPage(self):
		url = "http://www.nwanime.com/categories/"
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		animes = re.findall('<a\shref="([^"]+)">([^<]+)</a>&nbsp;&nbsp;.*?>(\d+)\svids', data, re.S)
		if animes:
			for (Url, Title, count) in animes:
				if int(count) > 0:
					self.streamList.append((decodeHtml(Title), Url))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.keyLocked = False
			self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		serienTitle = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		self.session.open(nwanimeEpisoden, auswahl, serienTitle)

	def keyAdd(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		muTitle = self['liste'].getCurrent()[0][0]
		muID = self['liste'].getCurrent()[0][1]

		if not fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist"):
			open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist","w").close()

		if fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist"):
			writePlaylist = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist","a")
			writePlaylist.write('"%s" "%s"\n' % (muTitle, muID))
			writePlaylist.close()
			message = self.session.open(MessageBoxExt, _("Selection was added to the watchlist."), MessageBoxExt.TYPE_INFO, timeout=3)

class nwanimeWatchlist(MPScreen):
	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"red" : self.keyDel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("NWANIME")
		self['ContentTitle'] = Label("Watchlist")
		self['F1'] = Label(_("Delete"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPlaylist)

	def loadPlaylist(self):
		self.streamList = []

		if not fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist"):
			open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist","w").close()

		if fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist"):
			readStations = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist","r")
			for rawData in readStations.readlines():
				data = re.findall('"(.*?)" "(.*?)"', rawData, re.S)
				if data:
					(stationName, stationLink) = data[0]
					self.streamList.append((stationName, stationLink))
			self.streamList.sort()
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			readStations.close()
			self.keyLocked = False
			self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return

		serienTitle = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		self.session.open(nwanimeEpisoden, auswahl, serienTitle)

	def keyDel(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return

		selectedName = self['liste'].getCurrent()[0][0]
		writeTmp = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist.tmp","w")
		if fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist"):
			readStations = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist","r")
			for rawData in readStations.readlines():
				data = re.findall('"(.*?)" "(.*?)"', rawData, re.S)
				if data:
					(stationName, stationLink) = data[0]
					if stationName != selectedName:
						writeTmp.write('"%s" "%s"\n' % (stationName, stationLink))
			readStations.close()
			writeTmp.close()
			shutil.move(config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist.tmp", config.mediaportal.watchlistpath.value+"mp_nwanime_watchlist")
			self.loadPlaylist()

class nwanimeEpisoden(MPScreen):
	def __init__(self, session, serienUrl, serienTitle):
		self.serienUrl = serienUrl
		self.serienTitle = serienTitle
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)

		self['title'] = Label("NWANIME")
		self['ContentTitle'] = Label(_("Episode Selection"))
		self['name'] = Label(self.serienTitle)

		self['Page'] = Label(_("Page:"))

		self.animeId = -1
		tmp_id = re.findall('/(\d+)/?\s*$', serienUrl)
		if tmp_id:
			self.animeId = int(tmp_id[0])
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.page = 1
		self.lastpage = 1

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.serienUrl
		if self.animeId >= 0:
			url = "http://www.nwanime.com/category_detail.php?page=%d&chid=%d&sortby=ep&ordertype=DESC&videoold=" % (self.page, self.animeId)
		getPage(url).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.getLastPage(data, 'class="paging">(.*?)</div>')
		# Mark Watches episodes
		self.streamList = []
		self.watched_liste = []
		self.mark_last_watched = []
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watched"):
			open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watched"):
			leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_nwanime_watched")
			if not leer == 0:
				self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched" , "r")
				for lines in sorted(self.updates_read.readlines()):
					line = re.findall('"(.*?)"', lines)
					if line:
						self.watched_liste.append("%s" % (line[0]))
				self.updates_read.close()
		episoden = re.findall('<a title=".*?href="(.*?)">(.*?)</a>.*?<div class="info_left">(.*?)</div>', data, re.S)
		details = re.findall('<div class="moduleEntryThumb-med" style="display:block;height:100%;width:100%;background: transparent url\((.*?)\).*?<div id="category_desc" name="category_desc" class="category_desc">.*?<hr>(.*?)</div>', data, re.S)

		if episoden:
			for (nwanimeUrl, nwanimeEpisode, info) in episoden:
				if re.search('preview', info, re.I):
					nwanimeEpisode += " (PREVIEW)"
				nwanimeEpisode = decodeHtml(nwanimeEpisode)
				checkname = self.generateEpisodenTitle(nwanimeEpisode)
				if checkname in self.watched_liste:
					self.streamList.append((nwanimeEpisode, nwanimeUrl, True))
				else:
					self.streamList.append((nwanimeEpisode, nwanimeUrl, False))
			self.ml.setList(map(self._defaultlistleftmarked, self.streamList))
			self.keyLocked = False
		if details:
			(cover, handlung) = details[0]
			handlung = stripAllTags(handlung).strip()
			self['handlung'].setText(decodeHtml(handlung))
			CoverHelper(self['coverArt']).getCover(cover)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][1]
		title = self['liste'].getCurrent()[0][0]
		self.session.open(nwanimeStreams, auswahl, self.generateEpisodenTitle(title), self.serienTitle, title)

	def generateEpisodenTitle(self, episodeTitle):
		return self.serienTitle + " - " + episodeTitle

class nwanimeStreams(MPScreen):

	def __init__(self, session, serienUrl, streamId, animeName, episodenTitel):
		self.serienUrl = serienUrl
		self.streamname = streamId
		self.animeName = animeName
		self.episodenTitel = episodenTitel
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("NWANIME")
		self['leftContentTitle'] = Label(_("Stream Selection"))
		self['ContentTitle'] = Label(_("Stream Selection"))
		self['name'] = Label(self.streamname)

		self.coverUrl = None
		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		getPage(self.serienUrl).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		raw =  re.findall('<div id="embed_code"(.*?)<div id="video_mirrors_mini"', data, re.S)
		if raw:
			streams = re.findall('<span class="lang"><a href="(.*?)".*?</a>.*?<a href=".*?" rel="nofollow">(\w+)',raw[0],re.S)
			if streams:
				for (nwanimeUrl,nwanimeHoster) in streams:
					if isSupportedHoster(nwanimeHoster, True):
						self.streamList.append((nwanimeHoster,nwanimeUrl))
				# remove duplicates
				self.streamList = list(set(self.streamList))
			if len(self.streamList) == 0:
				self.streamList.append(("No supported streams found.", None))
			self.ml.setList(map(self._defaultlisthoster, self.streamList))
			self.keyLocked = False
		episodenInfo = re.findall('.* (\d+)', self.episodenTitel)
		if episodenInfo:
			episodeNr = episodenInfo[0]
			handlungRaw = re.findall('Comments.*?<br\s*/>(<hr>)?\s*(.*?)\s*</div>', data, re.S)
			if handlungRaw:
				handlung = stripAllTags(handlungRaw[0][1]).strip()
				self['handlung'].setText(decodeHtml(handlung))
			coverRaw = re.findall('<a class="moduleEntryThumb-link" title="[^"]*Episode ' + re.escape(episodeNr) + '[^"]*".*?url\(\s*(.*?)\s*\)', data, re.S)
			if coverRaw:
				self.coverUrl = coverRaw[0]
				CoverHelper(self['coverArt']).getCover(self.coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][1]
		if auswahl:
			getPage(auswahl).addCallback(self.findStream).addErrback(self.dataError)

	def playfile(self, link):
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_nwanime_watched"):
			open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched","w").close()

		self.update_liste = []
		leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_nwanime_watched")
		if not leer == 0:
			self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched" , "r")
			for lines in sorted(self.updates_read.readlines()):
				line = re.findall('"(.*?)"', lines)
				if line:
					self.update_liste.append("%s" % (line[0]))
			self.updates_read.close()

			updates_read2 = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched" , "a")
			check = ("%s" % self.streamname)
			if not check in self.update_liste:
				updates_read2.write('"%s"\n' % (self.streamname))
				updates_read2.close()
		else:
			updates_read3 = open(config.mediaportal.watchlistpath.value+"mp_nwanime_watched" , "a")
			updates_read3.write('"%s"\n' % (self.streamname))
			updates_read3.close()
		self.session.open(SimplePlayer, [(self.streamname, link, self.coverUrl)], showPlaylist=False, ltype='nwanime')

	def findStream(self, data):
		test = re.findall('<div id="embed_holder".*?src="(.*?)"', data, re.I)
		test2 = re.findall('<div id="embed_holder".*?src=\'(.*?)\'', data, re.I)
		if test:
			get_stream_link(self.session).check_link(test[0], self.got_link)
		elif test2:
			get_stream_link(self.session).check_link(test2[0], self.got_link)
		else:
			message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def got_link(self, stream_url):
		self.playfile(stream_url.replace('&amp;','&'))