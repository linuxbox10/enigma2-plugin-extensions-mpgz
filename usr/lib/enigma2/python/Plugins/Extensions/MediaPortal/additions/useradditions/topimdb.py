# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

from kinoxto import *
from ddl_me import DDLME_FilmListeScreen

class timdbGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.searchKinoxCallback,
			"blue" : self.searchDdlmeCallback
		}, -1)

		self['title'] = Label("Top1000 IMDb")
		self['ContentTitle'] = Label(_("Selection:"))
		self['F2'] = Label("Kinox")
		self['F4'] = Label("ddl.me")

		self['Page'] = Label(_("Page:"))

		self.keyLocked = True
		self.filmliste = []
		self.page = 1
		self.lastpage = 20

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self.filmliste = []
		self.start = 1
		self.start = (self.page * 50) - 49

		url = "http://www.imdb.de/search/title?groups=top_1000&sort=user_rating,desc&start=%s" % str(self.start)
		getPage(url, headers={'Content-Type':'application/x-www-form-urlencoded', 'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:24.0) Gecko/20100101 Firefox/24.0', 'Accept-Language':'de-de,de;q=0.8,en-us;q=0.5,en;q=0.3'}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		movies = re.findall('class="lister-item.*?<img\salt="(.*?)".*?loadlate="(.*?\.jpg)".*?class="lister-item-index.*?>(.*?)\.</span>.*?class="lister-item-year.*?>\((\d+)\)</span.*?title="Users rated this (.*?\/10)', data, re.S)
		if movies:
			for title,image,place,year,rates in movies:
				image_raw = image.split('._V1_')
				image = "%s._V1_SX214_.jpg" % image_raw[0]
				self.filmliste.append((place, decodeHtml(title), year, rates, image))
				self.ml.setList(map(self.timdbEntry, self.filmliste))
			self.showInfos()
			self.keyLocked = False

	def showInfos(self):
		coverUrl = self['liste'].getCurrent()[0][4]
		self['page'].setText("%s / 20" % str(self.page))
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def searchKinoxCallback(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		url = "http://kinox.to/Search.html?q="
		self.session.open(kxSucheScreen, url, self.searchTitle)

	def searchDdlmeCallback(self):
		self.searchTitle = self['liste'].getCurrent()[0][1]
		url = "http://de.ddl.me/search_99/?q=%s" % urllib.quote(self.searchTitle.strip())
		self.session.open(DDLME_FilmListeScreen, url, "Suche...")