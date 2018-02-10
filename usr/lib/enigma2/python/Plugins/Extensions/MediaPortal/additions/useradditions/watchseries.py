# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

ws_url = "dwatchseries.to"

class watchseriesGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("Genre:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [('Series',"http://%s/letters/" % ws_url),
							('Newest Episodes Added',"http://%s/latest" % ws_url),
							('Popular Episodes Added This Week',"http://%s/new" % ws_url)]

		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['liste'].getCurrent()[0][0]
		streamGenreLink = self['liste'].getCurrent()[0][1]
		if streamGenreName == "Series":
			self.session.open(watchseriesSeriesLetterScreen, streamGenreLink, streamGenreName)
		else:
			self.session.open(watchseriesNewSeriesScreen, streamGenreLink, streamGenreName)

class watchseriesNewSeriesScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("%s:" % self.streamGenreName)

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		twAgentGetPage(self.streamGenreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('class="listings">(.*?)class="pagination">', data, re.S)
		eps = re.findall('<a\shref="(.*?)"\stitle="(.*?)".*?<span.*?>(.*?)</span>', parse.group(1), re.S)
		if eps:
			for url,title,epi in eps:
				season,episode = epi.split('x')
				title = title + ' - S'+season+'E'+episode
				self.genreliste.append((decodeHtml(title), url))
			self.ml.setList(map(self._defaultlistleft, self.genreliste))
			self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['liste'].getCurrent()[0][0]
		streamGenreLink = self['liste'].getCurrent()[0][1]
		self.session.open(watchseriesStreamListeScreen, streamGenreLink, streamGenreName)

class watchseriesSeriesLetterScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("Letter:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		abc = ["09","A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z"]
		for letter in abc:
			url = "http://%s/letters/%s" % (ws_url, letter)
			self.genreliste.append((letter, url))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		streamGenreName = self['liste'].getCurrent()[0][0]
		streamGenreLink = self['liste'].getCurrent()[0][1]
		self.session.open(watchseriesSeriesScreen, streamGenreLink, streamGenreName)

class watchseriesSeriesScreen(MPScreen, ThumbsHelper):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		ThumbsHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"5" : self.keyShowThumb,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("Letter - %s:" % self.streamGenreName)


		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		twAgentGetPage(self.streamGenreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		series = re.findall('<li><a href="(http://%s/serie/.*?)" title="(.*?)">.*?</li>' % ws_url, data, re.S)
		if series:
			self.filmliste = []
			for (url,title) in series:
				self.filmliste.append((decodeHtml(title),url))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.keyLocked = False
			self.th_ThumbsQuery(self.filmliste, 0, 1, None, None, 'property="og:image" content="(.*?)"', 1, 1, maxtoken=3)
			self.showInfos()

	def showInfos(self):
		filmName = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		twAgentGetPage(url).addCallback(self.getDetails).addErrback(self.dataError)

	def getDetails(self, data):
		image = re.findall('property="og:image" content="(.*?)"', data, re.S)
		details = re.findall('Description: </strong>(.*?)<br/>', data, re.S)
		handlung = ""
		if details:
				handlung = re.sub(r'<.*?>', '', details[0])
		if image:
				image = image[0]
		CoverHelper(self['coverArt']).getCover(image)
		self['handlung'].setText(decodeHtml(handlung))

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		self.session.open(watchseriesEpisodeListeScreen, streamLink, streamName)

class watchseriesEpisodeListeScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("Episodes:")
		self['name'] = Label(self.streamGenreName)


		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		twAgentGetPage(self.streamGenreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		parse = re.search('<ul class="listings(.*)class="sp-leader-bottom">', data, re.S)
		if parse:
			eps = re.findall('content="(http://%s/episode/.*?)"\s{0,1}/>.*?itemprop="name"\s{0,1}>(?:Episode\s\d+|)(?:&nbsp;){0,10}(.*?)<' % ws_url, parse.group(1), re.S)
			if eps:
				self.filmliste = []
				for (url, title) in eps:
					epinfo = re.findall('_s(\d+)_e(\d+).html', url)
					if epinfo:
						(season, episode) = epinfo[0]
						if int(season) < 10:
							season = "S0"+str(season)
						else:
							season = "S"+str(season)
						if int(episode) < 10:
							episode = "E0"+str(episode)
						else:
							episode = "E"+str(episode)
						episode = "%s%s - %s" % (season, episode, title)
						self.filmliste.append((decodeHtml(episode),url))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No episodes found!"), None))
		self.filmliste = list(set(self.filmliste))
		self.filmliste.sort()
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		streamName = self['liste'].getCurrent()[0][0]
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink:
			self.session.open(watchseriesStreamListeScreen, streamLink, streamName)

class watchseriesStreamListeScreen(MPScreen):

	def __init__(self, session, streamGenreLink, streamGenreName):
		self.streamGenreLink = streamGenreLink
		self.streamGenreName = streamGenreName
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("watchseries")
		self['ContentTitle'] = Label("Streams:")

		self.keyLocked = True
		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self['name'].setText(_("Please wait..."))
		twAgentGetPage(self.streamGenreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if re.match('.*?Sorry we do not have any links for this right now', data, re.S|re.I):
			self.filmliste = []
			self.filmliste.append(("There are no links available for this episode", None))
		else:
			streams = re.findall('class="download_link.*?<a target="_blank"\s+href=".*?cale.html\?r=(.*?)".*?title="(.*?)"', data, re.S)
			if streams:
				self.filmliste = []
				for (url,hostername) in streams:
					if isSupportedHoster(hostername, True):
						import base64
						url = base64.b64decode(url)
						self.filmliste.append((decodeHtml(hostername),url))
			if len(self.filmliste) == 0:
				self.filmliste.append((_("No supported streams found!"), None))
			else:
				self.keyLocked = False
		self.ml.setList(map(self._defaultlisthoster, self.filmliste))
		self['name'].setText(self.streamGenreName)

	def keyOK(self):
		if self.keyLocked:
			return
		streamLink = self['liste'].getCurrent()[0][1]
		if streamLink:
			get_stream_link(self.session).check_link(streamLink, self.got_link)

	def got_link(self, stream_url):
		self.session.open(SimplePlayer, [(self.streamGenreName, stream_url)], showPlaylist=False, ltype='watchseries')