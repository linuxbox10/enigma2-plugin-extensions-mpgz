# -*- coding: utf-8 -*-
###############################################################################################
#
#    MediaPortal for Dreambox OS
#
#    Coded by MediaPortal Team (c) 2013-2018
#
#  This plugin is open source but it is NOT free software.
#
#  This plugin may only be distributed to and executed on hardware which
#  is licensed by Dream Property GmbH. This includes commercial distribution.
#  In other words:
#  It's NOT allowed to distribute any parts of this plugin or its source code in ANY way
#  to hardware which is NOT licensed by Dream Property GmbH.
#  It's NOT allowed to execute this plugin and its source code or even parts of it in ANY way
#  on hardware which is NOT licensed by Dream Property GmbH.
#
#  This applies to the source code as a whole as well as to parts of it, unless
#  explicitely stated otherwise.
#
#  If you want to use or modify the code or parts of it,
#  you have to keep OUR license and inform us about the modifications, but it may NOT be
#  commercially distributed other than under the conditions noted above.
#
#  As an exception regarding execution on hardware, you are permitted to execute this plugin on VU+ hardware
#  which is licensed by satco europe GmbH, if the VTi image is used on that hardware.
#
#  As an exception regarding modifcations, you are NOT permitted to remove
#  any copy protections implemented in this plugin or change them for means of disabling
#  or working around the copy protections, unless the change has been explicitly permitted
#  by the original authors. Also decompiling and modification of the closed source
#  parts is NOT permitted.
#
#  Advertising with this plugin is NOT allowed.
#  For other uses, permission from the authors is necessary.
#
###############################################################################################

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *

BASE_URL = "https://bs.to"

class bsMain(MPScreen):

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

		self['title'] = Label("Burning-Series")
		self['ContentTitle'] = Label(_("Selection"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = False
		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		self.streamList.append(("Serien von A-Z","serien"))
		self.streamList.append(("Watchlist","watchlist"))
		self.ml.setList(map(self._defaultlistcenter, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		auswahl = self['liste'].getCurrent()[0][1]
		if auswahl == "serien":
			self.session.open(bsSerien)
		elif auswahl == "watchlist":
			self.session.open(bsWatchlist)

class bsSerien(MPScreen, SearchHelper):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr', widgets=('MP_widget_search',))
		SearchHelper.__init__(self)

		self["actions"] = ActionMap(["MP_Actions2", "MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"green" : self.keyAdd,
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
			"leftRepeated" : self.keyLeftRepeated
		}, -1)

		self['title'] = Label("Burning-Series")
		self['ContentTitle'] = Label("Serien A-Z")
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
		url = BASE_URL + "/api/series/"
		bstoken = bstkn(url)
		self.filmQ.put(url)
		if not self.eventL.is_set():
			self.eventL.set()
			self.loadPageQueued(headers={'User-Agent':'bs.android', 'BS-Token':bstoken})

	def loadPageData(self, data):
		serien = re.findall('series":"(.*?)","id":"(.*?)"', data, re.S)
		if serien:
			for (Title, ID) in serien:
				serie = ID
				cover = BASE_URL + "/public/img/cover/" + ID + ".jpg"
				self.streamList.append((decodeHtml(Title.replace('\/','/')),serie, cover, ID))
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.keyLocked = False
			self.loadPicQueued()

	def showInfos(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		title = self['liste'].getCurrent()[0][0]
		self['name'].setText(title)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		Title = self['liste'].getCurrent()[0][0]
		Url = self['liste'].getCurrent()[0][1]
		self.session.open(bsStaffeln, Title, Url)

	def keyAdd(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		muTitle = self['liste'].getCurrent()[0][0]
		muID = self['liste'].getCurrent()[0][1]
		fn = config.mediaportal.watchlistpath.value+"mp_bs_watchlist"
		if not fileExists(fn):
			open(fn,"w").close()
		try:
			writePlaylist = open(fn, "a")
			writePlaylist.write('"%s" "%s"\n' % (muTitle, muID))
			writePlaylist.close()
			message = self.session.open(MessageBoxExt, _("Selection was added to the watchlist."), MessageBoxExt.TYPE_INFO, timeout=3)
		except:
			pass

class bsWatchlist(MPScreen):

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

		self['title'] = Label("Burning-Series")
		self['ContentTitle'] = Label("Watchlist")
		self['F1'] = Label(_("Delete"))

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPlaylist)

	def loadPlaylist(self):
		self.streamList = []
		change = 0
		self.wl_path = config.mediaportal.watchlistpath.value+"mp_bs_watchlist"
		try:
			readStations = open(self.wl_path,"r")
			rawData = readStations.read()
			readStations.close()
			for m in re.finditer('"(.*?)" "(.*?)"', rawData):
				(stationName, stationLink) = m.groups()
				if stationLink.startswith('http'):
					change = 1
					break
				self.streamList.append((stationName, stationLink))
		except:
			pass

		if change == 1:
			url = BASE_URL + "/api/series/"
			bstoken = bstkn(url)
			getPage(url, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.convertPlaylist, rawData).addErrback(self.dataError)
		else:
			self.streamList.sort()
			self.ml.setList(map(self._defaultlistleft, self.streamList))
			self.keyLocked = False
			self.showInfos()

	def convertPlaylist(self, seriesdata, rawData):
		seriesdata = decodeHtml(seriesdata)
		try:
			writeTmp = open(self.wl_path,"w")
			for m in re.finditer('"(.*?)" "(.*?)"', rawData):
				(stationName, stationLink) = m.groups()
				if stationLink.startswith('http'):
					stationLink = self.getID(stationName, seriesdata)
					if stationLink:
						writeTmp.write('"%s" "%s"\n' % (stationName, stationLink))
					else:
						writeTmp.write('"%s" "%s"\n' % (stationName + " (N/A)", stationLink))
				else:
					writeTmp.write('"%s" "%s"\n' % (stationName, stationLink))
			writeTmp.close()
		except:
			return
		else:
			self.loadPlaylist()

	def getID(self, name, data):
		print "Searching ID for %s" % name
		ID = re.search('"%s","id":"(.*?)"' % name, data, re.S|re.I)
		if ID:
			print "Found ID (%s) for %s" % (ID.group(1), name)
			return ID.group(1)
		else:
			return False

	def showInfos(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		title = self['liste'].getCurrent()[0][0]
		id = self['liste'].getCurrent()[0][1]
		self.coverUrl = BASE_URL + "/public/img/cover/%s.jpg" % id
		CoverHelper(self['coverArt']).getCover(self.coverUrl)
		self['name'].setText(title)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		serienTitle = self['liste'].getCurrent()[0][0]
		auswahl = self['liste'].getCurrent()[0][1]
		self.session.open(bsStaffeln, serienTitle, auswahl)

	def keyDel(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return

		i = self['liste'].getSelectedIndex()
		c = j = 0
		l = len(self.streamList)
		try:
			f1 = open(self.wl_path, 'w')
			while j < l:
				if j != i:
					(stationName, stationLink) = self.streamList[j]
					f1.write('"%s" "%s"\n' % (stationName, stationLink))
				j += 1

			f1.close()
			self.loadPlaylist()
		except:
			pass

class bsStaffeln(MPScreen):

	def __init__(self, session, Title, Url):
		self.Url = BASE_URL + "/api/series/" + Url
		self.Title = Title
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Burning-Series")
		self['ContentTitle'] = Label(_("Season Selection"))
		self['name'] = Label(self.Title)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		url = self.Url + "/1"
		bstoken = bstkn(url)
		getPage(url, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		desc = re.search('description":"(.*?)","', data, re.S)
		if desc:
			self['handlung'].setText(decodeHtml(desc.group(1).replace('\\"','"')))
		else:
			self['handlung'].setText(_("No further information available!"))
		ID = re.search('"id":"(.*?)"', data, re.S)
		cover = BASE_URL + "/public/img/cover/" + ID.group(1) + ".jpg"
		movies = re.search('movies":"(.*?)"', data, re.S)
		if movies:
			movies = int(movies.group(1))
			if movies > 0:
				Staffel = "Staffel 0"
				buildurl = self.Url + "/0"
				self.streamList.append((Staffel,buildurl,cover))
		seasons = re.search('seasons":"(.*?)"', data, re.S)
		if seasons:
			season = int(seasons.group(1))
			for i in range(1,int(season)+1):
				Staffel = "Staffel %s" %i
				buildurl = self.Url + "/%s" %i
				self.streamList.append((Staffel,buildurl,cover))
		if len(self.streamList) == 0:
			self.streamList.append((_('No seasons found!'), None))
		self.ml.setList(map(self._defaultlistleft, self.streamList))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		coverUrl = self['liste'].getCurrent()[0][2]
		CoverHelper(self['coverArt']).getCover(coverUrl)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		staffel = self['liste'].getCurrent()[0][0]
		url = self['liste'].getCurrent()[0][1]
		cover = self['liste'].getCurrent()[0][2]
		self.session.open(bsEpisoden, url, staffel, self.Title, cover)

class bsEpisoden(MPScreen):

	def __init__(self, session, Url, Staffel, Title, Cover):
		self.Url = Url
		self.Staffel = Staffel
		self.Title = Title
		self.Cover = Cover
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("Burning-Series")
		self['ContentTitle'] = Label(_("Episode Selection"))
		self['name'] = Label(self.Title)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.streamList = []
		bstoken = bstkn(self.Url)
		getPage(self.Url, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		self.watched_liste = []
		self.mark_last_watched = []
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_bs_watched"):
			open(config.mediaportal.watchlistpath.value+"mp_bs_watched","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_bs_watched"):
			leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_bs_watched")
			if not leer == 0:
				self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_bs_watched" , "r")
				for lines in sorted(self.updates_read.readlines()):
					line = re.findall('"(.*?)"', lines)
					if line:
						self.watched_liste.append("%s" % (line[0]))
				self.updates_read.close()
		Staffel = self.Staffel.replace('Staffel ','')
		if int(Staffel) < 10:
			Staffel = "S0"+str(Staffel)
		else:
			Staffel = "S"+str(Staffel)

		data = re.search('.*?({.*})', data, re.S).group(1)
		data = data.replace('\r\n2000\r\n', '').replace('\r\n\r\nD67\r\n', '').replace('\r\nD67\r\n', '').replace('\r\n0\r\n\r\nE94\r\n', '')
		episoden = re.findall('german":"(.*?)","english":"(.*?)","epi":"(.*?)","watched', data, re.S)
		if episoden:
			Flag = ""
			for (TitleDE, TitleEN, epiID) in episoden:
				if int(epiID) < 10:
					epiID1= "E0"+str(epiID)
				else:
					epiID1= "E"+str(epiID)
				if TitleDE == "":
					Flag = "EN"
					Episode = Staffel + epiID1 + " - " + TitleEN
					check = (decodeHtml(self.Title)) + " - " + Staffel + epiID1 + " - " + (decodeHtml(TitleEN))
				else:
					Flag = "DE"
					Episode = Staffel + epiID1 + " - "  + TitleDE
					check = (decodeHtml(self.Title)) + " - " + Staffel + epiID1 + " - " + (decodeHtml(TitleDE))
				checkname = check
				checkname2 = check.replace('ä','ae').replace('ö','oe').replace('ü','ue').replace('Ä','Ae').replace('Ö','Oe').replace('Ü','Ue')
				if (checkname in self.watched_liste) or (checkname2 in self.watched_liste):
					self.streamList.append((decodeHtml(Episode),epiID,True,Flag))
				else:
					self.streamList.append((decodeHtml(Episode),epiID,False,Flag))
		if len(self.streamList) == 0:
			self.streamList.append((_('No episodes found!'), None, False))
		else:
			self.keyLocked = False
		self.ml.setList(map(self._defaultlistleftmarked, self.streamList))
		CoverHelper(self['coverArt']).getCover(self.Cover)
		self.showInfos()

	def showInfos(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		epiID = self['liste'].getCurrent()[0][1]
		url = self.Url + "/"
		finalcall = url + epiID
		bstoken = bstkn(finalcall)
		getPage(finalcall, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.callInfos).addErrback(self.dataError)

	def callInfos(self, data):
		desc = re.search('description":"(.*?)","', data, re.S)
		if desc:
			self['handlung'].setText(decodeHtml(desc.group(1).replace('\\"','"')))
		else:
			self['handlung'].setText(_("No further information available!"))

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		episode = self['liste'].getCurrent()[0][0]
		epiID = self['liste'].getCurrent()[0][1]
		url = self.Url + "/"
		finalcall = url + epiID
		Cover = self.Cover
		Staffel = self.Staffel
		self.session.openWithCallback(self.reloadList, bsStreams, finalcall, Cover, self.Title, episode, Staffel)

	def reloadList(self):
		self.keyLocked = True
		self.loadPage()

class bsStreams(MPScreen):

	def __init__(self, session, serienUrl, Cover, Title, Episode, Staffel):
		self.serienUrl = serienUrl
		self.Cover = Cover
		self.Title = Title
		self.episode = Episode
		self.staffel = Staffel
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"0" : self.closeAll,
			"ok" : self.keyOK,
			"cancel": self.keyCancel
		}, -1)

		self['title'] = Label("Burning-Series")
		self['leftContentTitle'] = Label(_("Stream Selection"))
		self['ContentTitle'] = Label(_("Stream Selection"))
		self['name'] = Label(self.Title)

		self.streamList = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml
		self.keyLocked = True
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		bstoken = bstkn(self.serienUrl)
		getPage(self.serienUrl, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.parseData).addErrback(self.dataError)

	def parseData(self, data):
		desc = re.search('description":"(.*?)","', data, re.S)
		if desc:
			self['handlung'].setText(decodeHtml(desc.group(1).replace('\\"','"')))
		else:
			self['handlung'].setText(_("No further information available!"))
		streams =  re.findall('"hoster":"(.*?)","id":"(.*?)"', data, re.S)
		if streams:
			for (Hoster,ID) in streams:
				Url = BASE_URL + "/api/watch/"
				if isSupportedHoster(Hoster, True):
					self.streamList.append((Hoster, ID, Url))
		if len(self.streamList) == 0:
			self.streamList.append((_('No supported streams found!'), None))
		else:
			self.keyLocked = False
		self.ml.setList(map(self._defaultlisthoster, self.streamList))
		CoverHelper(self['coverArt']).getCover(self.Cover)

	def keyOK(self):
		exist = self['liste'].getCurrent()
		if self.keyLocked or exist == None:
			return
		ID = self['liste'].getCurrent()[0][1]
		url = self['liste'].getCurrent()[0][2]
		auswahl = url + ID
		bstoken = bstkn(auswahl)
		getPage(auswahl, headers={'User-Agent':'bs.android', 'BS-Token':bstoken}).addCallback(self.findStream).addErrback(self.dataError)

	def playfile(self, link):
		if not re.search('\S[0-9][0-9]E[0-9][0-9]', self.Title, re.I):
			self.streamname = self.Title + " - " + self.episode
		else:
			self.streamname = self.Title
		if re.search('\sS[0-9][0-9]E[0-9][0-9]', self.streamname) and not re.search('-\sS[0-9][0-9]E[0-9][0-9]', self.streamname):
			new_title = ""
			splits = re.split('(S[0-9][0-9]E[0-9][0-9])', self.streamname, re.I)
			count = 0
			for split in splits:
				if count == 1:
					new_title += "- "
				new_title += split
				count += 1
			self.streamname = new_title

		if not fileExists(config.mediaportal.watchlistpath.value+"mp_bs_watched"):
			open(config.mediaportal.watchlistpath.value+"mp_bs_watched","w").close()
		self.update_liste = []
		leer = os.path.getsize(config.mediaportal.watchlistpath.value+"mp_bs_watched")
		if not leer == 0:
			self.updates_read = open(config.mediaportal.watchlistpath.value+"mp_bs_watched" , "r")
			for lines in sorted(self.updates_read.readlines()):
				line = re.findall('"(.*?)"', lines)
				if line:
					self.update_liste.append("%s" % (line[0]))
			self.updates_read.close()
			updates_read2 = open(config.mediaportal.watchlistpath.value+"mp_bs_watched" , "a")
			check = ("%s" % self.streamname)
			if not check in self.update_liste:
				print "update add: %s" % (self.streamname)
				updates_read2.write('"%s"\n' % (self.streamname))
				updates_read2.close()
			else:
				print "dupe %s" % (self.streamname)
		else:
			updates_read3 = open(config.mediaportal.watchlistpath.value+"mp_bs_watched" , "a")
			print "update add: %s" % (self.streamname)
			updates_read3.write('"%s"\n' % (self.streamname))
			updates_read3.close()
		self.session.open(SimplePlayer, [(self.streamname, link, self.Cover)], showPlaylist=False, ltype='burningseries', cover=True)

	def findStream(self, data):
		if "<html" in data:
			message = self.session.open(MessageBoxExt, _("Sorry this video is currently captcha protected, please try again later."), MessageBoxExt.TYPE_INFO, timeout=5)
		else:
			parse = re.findall('"hoster":"(.*?)","url":"(.*?)".*?"fullurl":"(.*?)"', data, re.S)
			if parse:
				if parse[0][2][:4] == "http":
					url = parse[0][2].replace('\\/','/')
				else:
					if parse[0][0] == "OpenLoad" or parse[0][0] == "OpenLoadHD":
						url = "https://openload.co/embed/" + parse[0][1].replace('\\/','/')
					else:
						message = self.session.open(MessageBoxExt, _("Received broken 'fullurl', please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)
				get_stream_link(self.session).check_link(url, self.got_link)
			else:
				message = self.session.open(MessageBoxExt, _("Broken URL parsing, please report to the developers."), MessageBoxExt.TYPE_INFO, timeout=3)

	def got_link(self, stream_url):
		self.playfile(stream_url)