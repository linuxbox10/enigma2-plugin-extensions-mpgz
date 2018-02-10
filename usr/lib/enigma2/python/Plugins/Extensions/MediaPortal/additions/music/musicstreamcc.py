# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage

MSCC_Version = "Musicstream.cc"

MSCC_siteEncoding = 'utf-8'

ms_cookies = CookieJar()

class show_MSCC_Genre(MPScreen):

	R_COMP_01 = re.compile('="list_td_right"><a href="(.*?)".*?<img alt="(.*?)"')

	def __init__(self, session, baseUrl='http://musicstream.cc', url=None, ctitle="Musikalben", red_key="Exit"):
		self.genre_url = url
		self.ctitle = ctitle

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"		: self.closeAll,
			"ok"    : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label(MSCC_Version)
		self['ContentTitle'] = Label(self.ctitle)
		self['name'] = Label(_("Selection:"))
		self['F1'] = Label(_("Exit"))

		self['F1'].setText = red_key
		self.base_url = baseUrl
		self.keylock = True
		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		if self.ctitle == "Musikalben":
			if config.mediaportal.restorelastservice.value == "1" and not config.mediaportal.backgroundtv.value:
				self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
			else:
				self.lastservice = None
			self.onClose.append(self.restoreLastService)

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.ml.setList(map(self.show_MSCC_GenreListEntry2, [('', _('Please wait...'), 0)]))
		if self.genre_url: 
			twAgentGetPage(self.base_url+self.genre_url).addCallback(self.parseFrameSrc).addErrback(self.dataError)
		else:
			twAgentGetPage(self.base_url).addCallback(self.parseFrameSrc).addErrback(self.dataError)

	def parseFrameSrc(self, data):
		m = re.search('<frame src="(.*?)"', data)
		if m:
			if '://' not in m.group(1):
				self.base_url += '/' + m.group(1)
			else:
				self.base_url = m.group(1)
			if self.base_url[-1] == '/':
				self.base_url = self.base_url[:-1]
			twAgentGetPage(self.base_url, cookieJar=ms_cookies).addCallback(self.parseData).addErrback(self.dataError)
		else:
			self.parseData(data)

	def dataError(self, error):
		printl(error,self,"E")
		self.ml.setList(map(self.show_MSCC_GenreListEntry2, [('', 'Keine Alben gefunden!', 0)]))

	def parseData(self, data):
		for m in self.R_COMP_01.finditer(data):
			u, a = m.groups()
			album = decodeHtml(a)
			if 'Sammlung ->' in album:
				self.genreliste.append((decodeHtml(u), album, 1))
			else:
				self.genreliste.append((decodeHtml(u), album, 2))

		if not self.genreliste:
			self.genreliste.append(('', 'Keine Alben gefunden !', 2))
		else:
			self.keylock = False
		self.ml.setList(map(self.show_MSCC_GenreListEntry, self.genreliste))

	def keyOK(self):
		if self.keylock:
			return

		musicfolder = self['liste'].getCurrent()[0][2] == 1
		album = self['liste'].getCurrent()[0][1]
		url = self['liste'].getCurrent()[0][0]

		if musicfolder:
			self.session.open(show_MSCC_Genre, self.base_url, url, album, "Zurück" )
		else:
			self.session.open(show_MSCC_ListScreen, self.base_url, url, album)

	def restoreLastService(self):
		if config.mediaportal.restorelastservice.value == "1" and not config.mediaportal.backgroundtv.value:
			self.session.nav.playService(self.lastservice)
		else:
			self.session.nav.stopService()

class show_MSCC_ListScreen(MPScreen):

	R_COMP_01 = re.compile('javascript: flashwin\(\'playwin\', \'(.*?)\'.*?<span.*?>(.*?)</')

	def __init__(self, session, baseUrl, album_url, album):

		self.album_url = album_url
		self.album = album
		self.baseUrl = baseUrl

		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0"			: self.closeAll,
			"ok" 		: self.keyOK,
			"cancel"	: self.keyCancel,
		}, -1)

		p = self.album.find('(')
		if p > 5:
			self.ctitle = self.album[:p].strip()
		else:
			self.ctitle = self.album

		self['title'] = Label(MSCC_Version)
		self['ContentTitle'] = Label(self.ctitle)
		self['name'] = Label(_("Selection:"))
		self['F1'] = Label(_("Exit"))

		self.keyLocked = True
		self.baseUrl = baseUrl

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.ml.setList(map(self.show_MSCC_ListEntry, [('', _('Please wait...'), '', '', '')]))
		url = self.baseUrl + self.album_url
		twAgentGetPage(url, cookieJar=ms_cookies).addCallback(self.parseData).addErrback(self.dataError)

	def dataError(self, error):
		printl(error,self,"E")
		self.ml.setList(map(self.show_MSCC_ListEntry, [('', _('No songs found!'), '', '', '')]))

	def parseData(self, data):
		m = re.search('="albumimg".*?src="(.*?)"', data)
		if m:
			img = m.group(1).replace('&amp;', '&')
		else:
			img = ''

		self.filmliste = []
		for m in self.R_COMP_01.finditer(data):
			u, t = m.groups()
			t = t.replace('_', ' ').replace('.mp3', '')
			self.filmliste.append(('', decodeHtml(t), self.ctitle, u.replace('&amp;', '&'), img))

		if len(self.filmliste) == 0:
			self.filmliste.append(('',_('No songs found!'),'','',''))
		else:
			menu_len = len(self.filmliste)
			self.keyLocked = False

		self.ml.setList(map(self.show_MSCC_ListEntry, self.filmliste))

	def keyOK(self):
		if self.keyLocked:
			return
		self.session.openWithCallback(self.close,
			MusicstreamccPlayer,
			self.baseUrl,
			self.filmliste,
			self['liste'].getSelectedIndex(),
			playAll = True,
			listTitle = self.ctitle
			)

class MusicstreamccPlayer(SimplePlayer):

	def __init__(self, session, baseUrl, playList, playIdx=0, playAll=True, listTitle=None):
		self.base_url = baseUrl
		self.chachepath = config.mediaportal.storagepath.value
		self.filescached = {}
		self.retrys = 0

		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, title_inr=1, ltype='musicstreamcc', autoScrSaver=True, cover=True, playerMode='MP3')

	def getVideo(self):
		url = self.base_url + self.playList[self.playIdx][3]
		twAgentGetPage(url, cookieJar=ms_cookies).addCallback(self.getV2).addErrback(self.dataError)

	def getV2(self, data):
		m = re.search('/mediaplayer.swf\?file=(.*?\.xml)', data)
		if m:
			url = self.base_url + urllib.unquote(m.group(1))
			twAgentGetPage(url, cookieJar=ms_cookies).addCallback(self.getV3).addErrback(self.dataError)
		else:
			m = re.search("file:\s*('|\")(.*?)('|\")", data, re.S)
			if m:
				url = m.group(2)
				self.playMP3(url)
			else:
				for m in re.finditer('<frame src="(.*?)">', data, re.S):
					if not self.retrys and 'index' in m.group(1):
						self.retrys += 1
						self.playList[self.playIdx][3] = self.playList[self.playIdx][3].replace('index.php', path)
						self.getVideo()
						return
				self.dataError('No MP3 Stream found:\n' + self.playList[self.playIdx][1])

	def getV3(self, data):
		m = re.search('<location>(.*?)</location>', data)
		if m:
			url = m.group(1)
			self.playMP3(url)
		else:
			self.dataError('Kein MP3 Stream gefunden:\n' + self.playList[self.playIdx][1])

	def playMP3(self, data):
		title = self.playList[self.playIdx][1]
		album = self.playList[self.playIdx][2]
		img = self.base_url + self.playList[self.playIdx][4]
		scArtist = ''
		scAlbum = album
		p = album.find(' - ')
		if p > 0:
			scArtist = album[:p].strip()
			scAlbum = album[p+3:].strip()

		p = title.find(' - ')
		if p > 0:
			scTitle = title[:p].strip()
		else:
			scTitle = title
		self.playStream(scTitle, data, album=scAlbum, artist=scArtist, imgurl=img)