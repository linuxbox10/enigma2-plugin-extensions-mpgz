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
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
from Plugins.Extensions.MediaPortal.resources.pininputext import PinInputExt
from Plugins.Extensions.MediaPortal.additions.porn.x2search4porn import toSearchForPorn

config.mediaportal.sharedir_size = ConfigText(default="", fixed_size=False)
config.mediaportal.sharedir_sort = ConfigText(default="", fixed_size=False)
config.mediaportal.sharedir_hoster = ConfigText(default="all Hosters;0", fixed_size=False)
config.mediaportal.sharedir_type = ConfigText(default="Video", fixed_size=False)

hosters =[]

class sharedirHelper():

	def keyType(self):
		if self.keyLocked:
			return
		if re.match(".*?2Search4Porn", self.Name):
			return
		if self.type != "Audio":
			self.type = "Audio"
		else:
			self.type = "Video"
		config.mediaportal.sharedir_type.value = self.type
		config.mediaportal.sharedir_type.save()
		configfile.save()
		self['F4'].setText(self.type)
		self.loadFirstPage()

	def keySize(self):
		if self.keyLocked:
			return
		rangelist = [['any Size', ''], ['Less than 50MB', '1'], ['50 MB to 500 MB', '2'], ['500 MB to 1 GB', '3'], ['Bigger than 1 GB', '4'], ['Bigger than 2 GB', '2048MB-99999MB'], ['Bigger than 3 GB', '3072MB-99999MB'], ['Bigger than 4 GB', '4096MB-99999MB'], ['Bigger than 5 GB', '5120MB-99999MB'], ['Bigger than 6 GB', '6144MB-99999MB'], ['Bigger than 7 GB', '7168MB-99999MB'], ['Bigger than 8 GB', '8192MB-99999MB']]
		self.session.openWithCallback(self.returnSize, ChoiceBoxExt, title=_('Select Size'), list = rangelist)

	def returnSize(self, data):
		if data:
			self.size = data[1]
			config.mediaportal.sharedir_size.value = self.size
			config.mediaportal.sharedir_size.save()
			configfile.save
			self['F3'].setText(data[0])
			self.loadFirstPage()

	def keySort(self):
		if self.keyLocked:
			return
		rangelist = [['Relevance', ''], ['Date +', 'da'], ['Date -', 'dd'], ['Size +', 'sa'], ['Size -', 'sd'], ['Filename +', 'na'], ['Filename -', 'nd']]
		self.session.openWithCallback(self.returnSort, ChoiceBoxExt, title=_('Select Sort order'), list = rangelist)

	def returnSort(self,data):
		if data:
			self.sort = data[1]
			config.mediaportal.sharedir_sort.value = self.sort
			config.mediaportal.sharedir_sort.save()
			configfile.save()
			self['F2'].setText(data[0])
			self.loadFirstPage()

	def keyHoster(self):
		if self.keyLocked:
			return
		rangelist =[]
		for hoster, id in self.hosters:
			rangelist.append([hoster, id])
		rangelist.sort()
		rangelist.insert(0, (['all Hosters', '0']))
		self.session.openWithCallback(self.returnHoster, ChoiceBoxExt, title=_('Select Hoster'), list = rangelist)

	def returnHoster(self, data):
		if data:
			self.hoster = data[1]
			config.mediaportal.sharedir_hoster.value = data[0]+";"+data[1]
			config.mediaportal.sharedir_hoster.save()
			configfile.save()
			self['F1'].setText(data[0])
			self.loadFirstPage()

	def loadFirstPage(self):
		try:
			self.page = 1
			self.filmliste = []
			self.loadPage()
		except:
			pass

	def errCancelDeferreds(self, error):
		myerror = error.getErrorMessage()
		if myerror:
			raise error

	def dataError(self, error):
		printl(error,self,"E")
		self.keyLocked = False

	def cancelSetValue(self):
		self.hoster = config.mediaportal.sharedir_hoster.value.split(";")[1]
		self.sort = config.mediaportal.sharedir_sort.value
		self.size = config.mediaportal.sharedir_size.value
		self['F1'].setText(config.mediaportal.sharedir_hoster.value.split(";")[0])
		rangelist = [['Relevance', ''], ['Date +', 'da'], ['Date -', 'dd'], ['Size +', 'sa'], ['Size -', 'sd'], ['Filename +', 'na'], ['Filename -', 'nd']]
		for item in rangelist:
			if item[1] == self.sort:
				self['F2'].setText(item[0])
		rangelist = [['any Size', ''], ['Less than 50MB', '1'], ['50 MB to 500 MB', '2'], ['500 MB to 1 GB', '3'], ['Bigger than 1 GB', '4'], ['Bigger than 2 GB', '2048MB-99999MB'], ['Bigger than 3 GB', '3072MB-99999MB'], ['Bigger than 4 GB', '4096MB-99999MB'], ['Bigger than 5 GB', '5120MB-99999MB'], ['Bigger than 6 GB', '6144MB-99999MB'], ['Bigger than 7 GB', '7168MB-99999MB'], ['Bigger than 8 GB', '8192MB-99999MB']]
		for item in rangelist:
			if item[1] == self.size:
				self['F3'].setText(item[0])
		self['F4'].setText(config.mediaportal.sharedir_type.value)

class sharedirMenueScreen(sharedirHelper, MPScreen):

	def __init__(self, session):
		self.Name = "--- Multi Search Engine ---"
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"0" : self.closeAll,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"red" : self.keyHoster,
			"green" : self.keySort,
			"yellow" : self.keySize,
			"blue" : self.keyType
		}, -1)

		self.hoster = config.mediaportal.sharedir_hoster.value.split(";")[1]
		self.sort = config.mediaportal.sharedir_sort.value
		self.size = config.mediaportal.sharedir_size.value
		self.type = config.mediaportal.sharedir_type.value
		self['title'] = Label("ShareDir")
		self['ContentTitle'] = Label("%s" % self.Name)
		self['F1'] = Label(config.mediaportal.sharedir_hoster.value.split(";")[0])
		self['F4'] = Label(self.type)
		self.keyLocked = True
		self.suchString = ''
		self.hosters = []
		self.pin = False

		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.getHosters)

	def getHosters(self):
		self.cancelSetValue()
		url = "http://sharedir.com"
		getPage(url).addCallback(self.loadHosters).addErrback(self.dataError)

	def loadHosters(self, data):
		hosterdata = re.findall('<input\stype="checkbox"\sname="dh_\d+"\sid="dh_\d+"\svalue="(\d+)".*?<label\sfor="dh_\d+">(.*?)</label>', data, re.S)
		if hosterdata:
			for (id, hostername) in hosterdata:
				if isSupportedHoster(hostername, True):
					self.hosters.append((hostername, id))
			global hosters
			hosters = self.hosters
		self.genreData()

	def genreData(self):
		self.genreliste.append(("--- Search ---", "callSuchen"))
		self.genreliste.append(("Search using Keyword List", "callKeywordList"))
		if config.mediaportal.showporn.value and config.mediaportal.show2search4porn.value:
			self.genreliste.append(("Search using 2Search4Porn List", "call2SearchList"))
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Pick = self['liste'].getCurrent()[0][1]
		if config.mediaportal.pornpin.value and not self.pin:
			self.pincheck()
		else:
			if Pick == "callSuchen":
				self.type = config.mediaportal.sharedir_type.value
				self.suchen()
			elif Pick == "callKeywordList":
				self.session.openWithCallback(self.cancelSetValue, sharedirKeyword, self.type)
			else:
				self.session.openWithCallback(self.cancelSetValue, call2SearchList)

	def SuchenCallback(self, callback = None, entry = None):
		Name = self['liste'].getCurrent()[0][0]
		Pick = self['liste'].getCurrent()[0][1]
		if callback is not None and len(callback):
			self.suchString = callback.replace(' ', '+')
			self.session.openWithCallback(self.cancelSetValue, sharedirListScreen, self.suchString, Name, self.hoster, self.type, self.size, self.sort)

	def pincheck(self):
		self.session.openWithCallback(self.pincheckok, PinInputExt, pinList = [(config.mediaportal.pincode.value)], triesEntry = self.getTriesEntry(), title = _("Please enter the correct PIN"), windowTitle = _("Enter PIN"))

	def getTriesEntry(self):
		return config.ParentalControl.retries.setuppin

	def pincheckok(self, pincode):
		if pincode:
			self.pin = True
			self.keyOK()

class call2SearchList(toSearchForPorn):

	def keyOK(self):
		if self.keyLocked:
			return
		if len(self.genreliste) > 0:
			search = self['liste'].getCurrent()[0][0].rstrip()
			Name = "2Search4Porn ShareDir"
			self.type = "Video"
			self.session.open(sharedirListScreen, search, Name, config.mediaportal.sharedir_hoster.value.split(";")[1], self.type , config.mediaportal.sharedir_size.value, config.mediaportal.sharedir_sort.value)

class sharedirKeyword(MPScreen):

	def __init__(self, session, type):
		self.type = type
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"red" : self.keyRed,
			"green" : self.keyGreen,
			"yellow" : self.keyYellow
		}, -1)

		self['title'] = Label("ShareDir")
		self['name'] = Label("Your Search Requests")
		self['ContentTitle'] = Label("Annoyed, typing in your search-words again and again?")

		self['F1'] = Label(_("Delete"))
		self['F2'] = Label(_("Add"))
		self['F3'] = Label(_("Edit"))
		self.keyLocked = True
		self.suchString = ''

		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.Searches)

	def Searches(self):
		self.genreliste = []
		self['liste'] = self.ml
		if not fileExists(config.mediaportal.watchlistpath.value+"mp_keywords"):
			open(config.mediaportal.watchlistpath.value+"mp_keywords","w").close()
		if fileExists(config.mediaportal.watchlistpath.value+"mp_keywords"):
			fobj = open(config.mediaportal.watchlistpath.value+"mp_keywords","r")
			for line in fobj:
				self.genreliste.append((line, None))
			fobj.close()
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))
			self.keyLocked = False

	def SearchAdd(self):
		suchString = ""
		self.session.openWithCallback(self.SearchAdd1, VirtualKeyBoardExt, title = (_("Enter Search")), text = suchString, is_dialog=True, auto_text_init=True)

	def SearchAdd1(self, suchString):
		if suchString is not None and suchString != "":
			self.genreliste.append((suchString,None))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))

	def SearchEdit(self):
		if len(self.genreliste) > 0:
			suchString = self['liste'].getCurrent()[0][0].rstrip()
			self.session.openWithCallback(self.SearchEdit1, VirtualKeyBoardExt, title = (_("Enter Search")), text = suchString, is_dialog=True, auto_text_init=True)

	def SearchEdit1(self, suchString):
		if suchString is not None and suchString != "":
			pos = self['liste'].getSelectedIndex()
			self.genreliste.pop(pos)
			self.genreliste.insert(pos,(suchString,None))
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))

	def keyOK(self):
		if self.keyLocked:
			return
		if len(self.genreliste) > 0:
			search = self['liste'].getCurrent()[0][0].rstrip()
			Name = "Keywords ShareDir"
			self.session.open(sharedirListScreen, search, Name, config.mediaportal.sharedir_hoster.value.split(";")[1], self.type , config.mediaportal.sharedir_size.value, config.mediaportal.sharedir_sort.value)

	def keyRed(self):
		if self.keyLocked:
			return
		if len(self.genreliste) > 0:
			self.genreliste.pop(self['liste'].getSelectedIndex())
			self.ml.setList(map(self._defaultlistcenter, self.genreliste))

	def keyGreen(self):
		if self.keyLocked:
			return
		self.SearchAdd()

	def keyYellow(self):
		if self.keyLocked:
			return
		self.SearchEdit()

	def keyCancel(self):
		if self.keyLocked:
			return
		self.genreliste.sort(key=lambda t : t[0].lower())
		fobj_out = open(config.mediaportal.watchlistpath.value+"mp_keywords","w")
		x = len(self.genreliste)
		if x > 0:
			for c in range(x):
				writeback = self.genreliste[c][0].rstrip()+"\n"
				fobj_out.write(writeback)
			fobj_out.close()
		else:
			os.remove(config.mediaportal.watchlistpath.value+"mp_keywords")
		self.close()

class sharedirListScreen(sharedirHelper, MPScreen):

	def __init__(self, session, suchString, Name, hoster, type, size, sort):
		self.suchString = suchString
		self.Name = Name
		self.type = type
		self.sort = sort
		self.size = size
		self.hoster = hoster
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"cancel" : self.keyCancel,
			"0" : self.closeAll,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"red" : self.keyHoster,
			"green" : self.keySort,
			"yellow" : self.keySize,
			"blue" : self.keyType
		}, -1)

		self['title'] = Label("ShareDir")
		self['ContentTitle'] = Label("%s / Search for: %s" % (self.Name, self.suchString))
		self['Page'] = Label(_("Page:"))
		self['F1'] = Label(config.mediaportal.sharedir_hoster.value.split(";")[0])
		self['F4'] = Label(self.type)

		self.keyLocked = True
		self.page = 1
		self.lastpage = 1
		self.hosters = hosters

		self.filmliste = []
		self.Cover = ''
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.deferreds = []

		self.ds = defer.DeferredSemaphore(tokens=1)
		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.cancelSetValue()
		if re.match(".*?2Search4Porn", self.Name):
			self['F4'].setText("")
		if self.hoster == '0':
			for items in self.hosters:
				self.hoster = self.hoster + ",%s" % items[1]
			if self.hoster[0] == ',':
				self.hoster = self.hoster[1:]
		self.keyLocked = True
		self.filmliste = []
		self.ml.setList(map(self.searchallucMultiListEntry, self.filmliste))
		self['handlung'].setText('')
		self['name'].setText(_('Please wait...'))
		Url = "%s" % self.suchString.replace(" ", "+")
		if self.sort != '':
			Url = "%s&sort=%s" % (Url, self.sort)
		if self.size != '':
			Url = "%s&size=%s" % (Url, self.size)
		if Url:
			if Url[0] == '+':
				Url = Url[1:]
		if self.type == "Audio":
			ftype = "3"
		else:
			ftype = "4"
		for items in self.deferreds:
			items.cancel()
		dsUrl = "http://sharedir.com/index.php?s=%s&start=%s&ftype=%s&stype=%s" % (Url, self.page, ftype, self.hoster)
		d = self.ds.run(getPage, dsUrl, agent=std_headers, timeout=5).addCallback(self.loadPageData).addErrback(self.dataError)
		self.deferreds.append(d)

	def loadPageData(self, data):
		self.getLastPage(data, 'id="page_links"(.*?)</div>', '.*>\[{0,1}\s{0,1}(\d+)[\]{0,1}\s{0,1}|<]')
		preparse = re.search('class="sp_header">(.*?)id="footer', data, re.S)
		if preparse:
			Movies = re.findall('class="big"\stitle="(.*?)"\shref="(.*?)".*?class="item_info"><div>(.*?)</div>.*?extension:\s<b>(.*?)</b></div><div><b>(.*?)</div>.*?class="rdonly">(.*?)</div>.*?class="item_src info_in">(.*?)<span>', preparse.group(1), re.S)
			if Movies:
				for Title, Url, Hostername, Ext, Size, Date, Source in Movies:
					Url = "http://sharedir.com%s" % Url
					if isSupportedHoster(Hostername, True):
						Size = stripAllTags(Size).strip()
						self.filmliste.append((decodeHtml(Title), Url, Hostername, Ext, Size, Date, Source.strip("www.")))
		if len(self.filmliste) == 0:
			self.filmliste.append((_("No Files found!"), None, '', '', '', ''))
		self.ml.setList(map(self.searchallucMultiListEntry, self.filmliste))
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Hoster = self['liste'].getCurrent()[0][2]
		Ext = self['liste'].getCurrent()[0][3]
		Size = self['liste'].getCurrent()[0][4]
		Date = self['liste'].getCurrent()[0][5]
		Source = self['liste'].getCurrent()[0][6]
		Handlung = "Extension: %s\nDate: %s\nSize: %s\nHoster: %s\nSource: %s\n" % (Ext, Date, Size, Hoster, Source)
		self['name'].setText(Title)
		self['handlung'].setText(Handlung)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = self['liste'].getCurrent()[0][1]
		if Link == None:
			return
		self.keyLocked = True
		getPage(Link, agent=std_headers).addCallback(self.getHosterLink).addErrback(self.noVideoError).addErrback(self.dataError)

	def getHosterLink(self, data):
		streams = re.search('<pre\sid="dirlinks"\sclass="dl_normal clr">(.*?).</pre>', data, re.S)
		if streams:
			Hoster = self['liste'].getCurrent()[0][2]
			self.get_redirect(streams.group(1))
		self.keyLocked = False

	def noVideoError(self, error):
		try:
			if error.value.status == '404':
				message = self.session.open(MessageBoxExt, _("No link found."), MessageBoxExt.TYPE_INFO, timeout=3)
		except:
			pass
		self.keyLocked = False
		raise error

	def keyCancel(self):
		for items in self.deferreds:
			items.cancel()
		self.deferreds = []
		self.close()

	def get_redirect(self, url):
		get_stream_link(self.session).check_link(url, self.got_link)

	def got_link(self, stream_url):
		self.keyLocked = False
		Title = self['liste'].getCurrent()[0][0]
		self.session.open(SimplePlayer, [(Title, stream_url)], showPlaylist=False, ltype='sharedir')