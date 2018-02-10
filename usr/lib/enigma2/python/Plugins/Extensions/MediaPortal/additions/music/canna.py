# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.cannalink import CannaLink

class cannaGenreScreen(MPScreen):

	def __init__(self, session):

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Canna.to")
		self['ContentTitle'] = Label(_("Albums:"))

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [
			('Playlist',None,"3"),
			('Germany Top 100',"http://ua.canna.to/canna/single.php","1"),
			('Austria Top 75',"http://ua.canna.to/canna/austria.php","1"),
			('Swiss Top 100',"http://ua.canna.to/canna/swiss.php","1"),
			('US Top 100',"http://ua.canna.to/canna/ussingle.php","1"),
			('UK Top 40',"http://ua.canna.to/canna/uksingle.php","1"),
			('Germany Black Top 40',"http://ua.canna.to/canna/black.php","1"),
			('Germany ODC Top 50',"http://ua.canna.to/canna/odc.php","1"),
			('Rock/Metal Top 40',"http://ua.canna.to/canna/metalsingle.php","1"),
			('Party Schlager Top 30',"http://ua.canna.to/canna/psc.php","1"),
			('US Country Top 25',"http://ua.canna.to/canna/country.php","1"),
			('Jamaican Reggae Top 25',"http://ua.canna.to/canna/reggae.php","1"),
			('Germany Jahrescharts',"http://ua.canna.to/canna/jahrescharts.php","2"),
			('Austria Jahrescharts',"http://ua.canna.to/canna/austriajahrescharts.php","2"),
			('Black Jahrescharts',"http://ua.canna.to/canna/blackjahrescharts.php","2"),
			('Dance Jahrescharts',"http://ua.canna.to/canna/dancejahrescharts.php","2"),
			('Party Schlager Jahrescharts',"http://ua.canna.to/canna/partyjahrescharts.php","2"),
			('Swiss Jahrescharts',"http://ua.canna.to/canna/swissjahrescharts.php","2")]

		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		cannahdGenre = self['liste'].getCurrent()[0][0]
		cannahdUrl = self['liste'].getCurrent()[0][1]
		cannahdID = self['liste'].getCurrent()[0][2]

		if cannahdID == "1":
			self.session.open(cannaMusicListeScreen, cannahdGenre, cannahdUrl)
		elif cannahdID == "2":
			self.session.open(cannaJahreScreen, cannahdGenre, cannahdUrl)
		elif cannahdID == "3":
			self.session.open(cannaPlaylist, cannahdGenre)

class cannaPlaylist(MPScreen):

	def __init__(self, session, genreName):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')
		self.genreName = genreName

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"red": self.keyDel
		}, -1)

		self.keyLocked = True
		self["title"] = Label("Canna.to")
		self['ContentTitle'] = Label(self.genreName)
		self['F1'] = Label(_("Delete"))

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPlaylist)

	def loadPlaylist(self):
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_canna_playlist"):
			open(config.mediaportal.watchlistpath.value+"mp_canna_playlist","w").close()

		leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_canna_playlist")
		if not leer == 0:
			self.filmliste = []
			self.songs_read = open(config.mediaportal.watchlistpath.value+"mp_canna_playlist" , "r")
			for lines in sorted(self.songs_read.readlines()):
				line = re.findall('"(.*?)" "(.*?)"', lines)
				if line:
					(read_song, read_url) = line[0]
					self.filmliste.append((decodeHtml(read_song),read_url))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.keyLocked = False
			self.songs_read.close()
		else:
			self.filmliste = []
			self.filmliste.append((_("No entries in the playlist available!"),None))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))

	def keyOK(self):
		if self.keyLocked:
			return
		idx = self['liste'].getSelectedIndex()
		self.session.open(CannaPlayer, self.filmliste, int(idx), True, self.genreName)

	def keyDel(self):
		if self.keyLocked:
			return

		cannaName = self['liste'].getCurrent()[0][0]

		writeTmp = open(config.mediaportal.watchlistpath.value+"mp_canna_playlist.tmp","w")
		if fileExists(config.mediaportal.watchlistpath.value+"mp_canna_playlist"):
			readPlaylist = open(config.mediaportal.watchlistpath.value+"mp_canna_playlist","r")
			for rawData in readPlaylist.readlines():
				data = re.findall('"(.*?)" "(.*?)"', rawData, re.S)
				if data:
					(read_name, read_url) = data[0]
					if read_name != cannaName:
						writeTmp.write('"%s" "%s"\n' % (read_name, read_url))
			readPlaylist.close()
			writeTmp.close()
			shutil.move(config.mediaportal.watchlistpath.value+"mp_canna_playlist.tmp", config.mediaportal.watchlistpath.value+"mp_canna_playlist")
			self.loadPlaylist()

class cannaMusicListeScreen(MPScreen):

	def __init__(self, session, genreName, genreLink, type=""):
		self.genreLink = genreLink
		self.genreName = genreName
		self.type = type
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel,
			"green": self.keyAdd
		}, -1)

		self.keyLocked = True
		self["title"] = Label("Canna.to")
		self['ContentTitle'] = Label(self.genreName)
		self['F2'] = Label(_("Add to Playlist"))

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		getPage(self.genreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		if self.type == "Jahre":
			raw = re.findall('<td align="left" style="border-style:solid; border-width:1px;">(.*?)>>  Player  <<', data, re.S)
			if raw:
				for each in raw:
					match = re.findall('<font size="1" face="Arial"><b>(.*?)</b></font>.*?<font size="1" face="Arial"><b>(.*?)</b></font>.*?(jc_player.php.*?)\'', each, re.S)
					if match:
						for (artist,title,url) in match:
							url = "http://ua.canna.to/canna/"+url
							title = "%s - %s" % (artist, title)
							self.filmliste.append((decodeHtml(title),url))
		else:
			match = re.findall('<tr>.*?<font>(.*?)</font>.*?class="obutton" onClick="window.open..(.*?)...CannaPowerChartsPlayer.*?</tr>', data, re.S)
			if match:
				for title,url in match:
					url = "http://ua.canna.to/canna/"+url
					self.filmliste.append((decodeHtml(title),url))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.keyLocked = False

	def keyAdd(self):
		if self.keyLocked:
			return

		cannaName = self['liste'].getCurrent()[0][0]
		cannaUrl = self['liste'].getCurrent()[0][1]

		if not fileExists(config.mediaportal.watchlistpath.value+"mp_canna_playlist"):
			open(config.mediaportal.watchlistpath.value+"mp_canna_playlist","w").close()

		if not self.checkPlaylist(cannaName):
			if fileExists(config.mediaportal.watchlistpath.value+"mp_canna_playlist"):
				writePlaylist = open(config.mediaportal.watchlistpath.value+"mp_canna_playlist","a")
				writePlaylist.write('"%s" "%s"\n' % (cannaName, cannaUrl))
				writePlaylist.close()
				message = self.session.open(MessageBoxExt, _("added"), MessageBoxExt.TYPE_INFO, timeout=2)
		else:
			message = self.session.open(MessageBoxExt, _("Song already exists."), MessageBoxExt.TYPE_INFO, timeout=2)

	def checkPlaylist(self, song):
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_canna_playlist"):
			open(config.mediaportal.watchlistpath.value+"mp_canna_playlist","w").close()
			return False
		else:
			leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_canna_playlist")
			if not leer == 0:
				self.dupelist = []
				self.songs_read = open(config.mediaportal.watchlistpath.value+"mp_canna_playlist" , "r")
				for lines in sorted(self.songs_read.readlines()):
					line = re.findall('"(.*?)" "(.*?)"', lines)
					if line:
						(read_song, read_url) = line[0]
						self.dupelist.append((read_song))
				self.songs_read.close()

				if song in self.dupelist:
					return True
				else:
					return False
			else:
				return False

	def keyOK(self):
		if self.keyLocked:
			return
		idx = self['liste'].getSelectedIndex()
		self.session.open(CannaPlayer, self.filmliste, int(idx), True, self.genreName)

class cannaJahreScreen(MPScreen):

	def __init__(self, session, genreName, genreLink):
		self.genreLink = genreLink
		self.genreName = genreName

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("Canna.to")
		self['ContentTitle'] = Label(_("Year:"))

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		getPage(self.genreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		match = re.findall('<b><font face="Arial" size="5" color="#FFCC00"><a href="(.*?)">(.*?)</a></font></b>', data, re.S)
		if match:
			for url, title in match:
				url = "http://ua.canna.to/canna/"+url
				self.filmliste.append((decodeHtml(title),url))
			self.filmliste.reverse()
			self.ml.setList(map(self._defaultlistcenter, self.filmliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		cannahdGenre = self['liste'].getCurrent()[0][0]
		cannahdUrl = self['liste'].getCurrent()[0][1]
		self.session.open(cannaMusicListeScreen, cannahdGenre, cannahdUrl, "Jahre")

class CannaPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None):
		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='canna')
		self.listTitle = listTitle

	def getVideo(self):
		title = self.playList[self.playIdx][self.title_inr]
		url = self.playList[self.playIdx][1]

		cannaName = title
		if re.match('.*?-', cannaName):
			playinfos = cannaName.split(' - ')
			if playinfos:
				if len(playinfos) == 2:
					artist = playinfos[0]
					title = playinfos[1]
			else:
				playinfos = cannaName.split('-')
				if playinfos:
					if len(playinfos) == 2:
						artist = playinfos[0]
						title = playinfos[1]
		else:
			artist = ''
			title = cannaName

		CannaLink(self.session).getLink(self.playStream, self.dataError, title, artist, self.listTitle, url, None)