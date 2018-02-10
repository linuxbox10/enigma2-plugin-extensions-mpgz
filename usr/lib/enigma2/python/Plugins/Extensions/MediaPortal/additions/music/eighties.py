# -*- coding: utf-8 -*-
from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.eightieslink import EightiesLink

class eightiesGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok"    : self.keyOK,
			"0" : self.closeAll,
			"cancel": self.keyCancel
		}, -1)

		self.keyLocked = True
		self['title'] = Label("80s & 90s Music")
		self['ContentTitle'] = Label("Genre:")

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.genreliste = [
			('80s Music',"http://www.80smusicvids.com/"),
			('90s Music',"http://www.90smusicvidz.com/")]
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		eightiesName = self['liste'].getCurrent()[0][0]
		eightiesUrl = self['liste'].getCurrent()[0][1]
		self.session.open(eightiesMusicListeScreen, eightiesName, eightiesUrl)

class eightiesMusicListeScreen(MPScreen):

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
		self["title"] = Label(self.genreName)

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		if re.match('.*?80smusicvids.com', self.genreLink, re.S):
			self.baseurl = "http://www.80smusicvids.com/"
			self.token = '80smusicvids'
		else:
			self.baseurl = "http://www.90smusicvidz.com/"
			self.token = '90smusicvidz'
		getPage(self.genreLink).addCallback(self.loadPageData).addErrback(self.dataError)

	def loadPageData(self, data):
		vids = re.findall('<a target="_self" href="(.*?)">(.*?)</a><br>', data, re.S)
		if vids:
			for url,title in vids:
				url = "%s%s" % (self.baseurl, url.replace(' ','%20'))
				self.filmliste.append((decodeHtml(title),url))
			self.ml.setList(map(self._defaultlistleft, self.filmliste))
			self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		idx = self['liste'].getSelectedIndex()
		self.session.open(EightiesPlayer, self.filmliste, int(idx), True, self.genreName, self.token)

class EightiesPlayer(SimplePlayer):

	def __init__(self, session, playList, playIdx=0, playAll=True, listTitle=None, token=""):
		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=playAll, listTitle=listTitle, ltype='eighties')
		self.token = token
		self.listTitle = listTitle
		self.eightieslink = EightiesLink(self.session)

	def getVideo(self):
		title = self.playList[self.playIdx][self.title_inr]
		url = self.playList[self.playIdx][1]

		playinfos = title
		if re.match('.*?-', playinfos):
			playinfos = playinfos.split(' - ')
			if playinfos:
				if len(playinfos) == 2:
					scArtist = playinfos[0]
					scTitle = playinfos[1]
				else:
					playinfos = playinfos[0].split('-')
					if playinfos:
						if len(playinfos) == 2:
							scArtist = playinfos[0].strip()
							scTitle = playinfos[1].strip()
		else:
			scArtist = ''
			scTitle = playinfos

		self.eightieslink.getLink(self.playStream, self.dataError, scTitle, scArtist, self.listTitle, url, self.token, None)