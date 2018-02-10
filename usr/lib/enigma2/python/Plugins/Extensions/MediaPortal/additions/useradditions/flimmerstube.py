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
from Plugins.Extensions.MediaPortal.resources.youtubeplayer import YoutubePlayer

BASE_URL="http://flimmerstube.com"

class flimmerstubeGenreScreen(MPScreen):

	def __init__(self, session):
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft
		}, -1)

		self['title'] = Label("FlimmerStube.com")
		self['ContentTitle'] = Label("Genre:")

		self.keyLocked = True
		self.suchString = ''
		self.genreliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.layoutFinished)

	def layoutFinished(self):
		self.keyLocked = True
		getPage(BASE_URL).addCallback(self.genreData).addErrback(self.dataError)

	def genreData(self, data):
		parse = re.search('<section class="sidebox">(.*)</section>',data, re.S)
		cats = re.findall('<a class=\'.*?\' href="(.*?)" >(.*?)(?:</a>|\/)', parse.group(1), re.S)
		for (url, title) in cats:
			if title != "Horror Serien":
				self.genreliste.append((title, url))
		self.genreliste.sort()
		self.ml.setList(map(self._defaultlistcenter, self.genreliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False

	def keyOK(self):
		if self.keyLocked:
			return
		Name = self['liste'].getCurrent()[0][0]
		Link = self['liste'].getCurrent()[0][1]
		self.session.open(flimmerstubeFilmScreen, Link, Name)

class flimmerstubeFilmScreen(MPScreen):

	def __init__(self, session, Link, Name):
		self.Link = Link
		self.Name = Name
		MPScreen.__init__(self, session, skin='MP_PluginDescr')

		self["actions"] = ActionMap(["MP_Actions"], {
			"ok" : self.keyOK,
			"0" : self.closeAll,
			"cancel" : self.keyCancel,
			"up" : self.keyUp,
			"down" : self.keyDown,
			"right" : self.keyRight,
			"left" : self.keyLeft,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown,
			"green" : self.keyPageNumber
		}, -1)

		self['title'] = Label("FlimmerStube.com")
		self['ContentTitle'] = Label("Genre: %s" % self.Name)
		self['F2'] = Label(_("Page"))

		self['Page'] = Label(_("Page:"))
		self.keyLocked = True
		self.lastKat = ''
		self.page = 1

		self.filmliste = []
		self.ml = MenuList([], enableWrapAround=True, content=eListboxPythonMultiContent)
		self['liste'] = self.ml

		self.onLayoutFinish.append(self.loadPage)

	def loadPage(self):
		self.keyLocked = True
		self['name'].setText(_('Please wait...'))
		self.filmliste = []
		url = "%s%s/*%s" % (BASE_URL, self.Link, str(self.page))
		getPage(url).addCallback(self.loadData).addErrback(self.dataError)

	def loadData(self, data):
		lastp = re.search('id="num_entries">(.*?)</span>', data, re.S)
		if lastp:
			lastp = lastp.group(1)
			cat = self.Link
			if float(float(lastp)/15).is_integer():
				lastp = float(lastp) / 15
			else:
				lastp = round((float(lastp) / 15) + 0.5)
			self.lastpage = int(lastp)
		else:
			self.lastpage = 1
		self['page'].setText(str(self.page) + ' / ' + str(self.lastpage))
		vSearch = re.search('<section class="content">(.*?)<aside class="sidebar">',data,re.S)
		titles = re.findall('<h4 class="ve-title">.*?<a href="(.*?)">.*?</a>.*?</h4>.*?<div class="ve-screen" title="(.*?)".*?style="background-image: url\((.*?)\);',vSearch.group(1), re.S)
		if titles:
			for (url, title, img) in titles:
				title = title.replace(' - Stream - Deutsch','').replace(' - Stream','').replace(' - DDR Scifi','').replace(' - Giallo','').replace(' - Scifi','').replace(' - Komödie','').replace(' - Exploitation','').replace(' - Horror Komödie','').replace(' - Horror Doku','').replace(' - Horror','').replace(' - Endzeit','').replace(' - Fantasy','').replace(' - Doku','').replace(' - Deutsch','').replace(' - Western','').replace(' - Krimi','').replace(' - Biografie','').replace(' - HD','').replace(' - Tormented','').replace(' - Asia Horror','').replace(' - STream','').replace(' German/Deutsch','').strip('-Horror')
				if not ('TV Serie' or 'Mehrteiler') in title:
					self.filmliste.append((decodeHtml(title), url, img))
		self.ml.setList(map(self._defaultlistleft, self.filmliste))
		self.ml.moveToIndex(0)
		self.keyLocked = False
		self.showInfos()

	def showInfos(self):
		Title = self['liste'].getCurrent()[0][0]
		Image = self['liste'].getCurrent()[0][2]
		self['name'].setText(Title)
		CoverHelper(self['coverArt']).getCover(Image)

	def keyOK(self):
		if self.keyLocked:
			return
		Link = "%s%s" % (BASE_URL, self['liste'].getCurrent()[0][1])
		self.keyLocked = True
		getPage(Link).addCallback(self.getVideoData).addErrback(self.dataError)

	def getVideoData(self, data):
		ytUrl = re.findall('"http[s]?://www.youtube.com/(v|embed)/(.*?)\?.*?"', data, re.S)
		if ytUrl:
			Title = self['liste'].getCurrent()[0][0]
			self.session.open(YoutubePlayer,[(Title, ytUrl[0][1], None)],playAll= False,showPlaylist=False,showCover=False)
		else:
			self.session.open(MessageBoxExt, _('No supported streams found!'), MessageBoxExt.TYPE_INFO, timeout=5)
		self.keyLocked = False