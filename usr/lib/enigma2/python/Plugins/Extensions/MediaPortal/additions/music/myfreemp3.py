# -*- coding: utf-8 -*-

from Plugins.Extensions.MediaPortal.plugin import _
from Plugins.Extensions.MediaPortal.resources.imports import *
from Plugins.Extensions.MediaPortal.resources.choiceboxext import ChoiceBoxExt
from Plugins.Extensions.MediaPortal.resources.keyboardext import VirtualKeyBoardExt
import Queue
import threading
from Plugins.Extensions.MediaPortal.resources.menuhelper import MenuHelper
from Plugins.Extensions.MediaPortal.resources.simple_lru_cache import SimpleLRUCache
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage, TwAgentHelper

try:
	from Plugins.Extensions.MediaPortal.resources import cfscrape
except:
	cfscrapeModule = False
else:
	cfscrapeModule = True

try:
	import requests
except:
	requestsModule = False
else:
	requestsModule = True

import urlparse
import thread

mfmp3_cookies = CookieJar()
mfmp3_ck = {}
mfmp3_agent = ''
glob_historyLRUCache = SimpleLRUCache(100, config.mediaportal.watchlistpath.value + 'mp_mfmp3_history')
BASE_URL = "http://www.myfreemp3.fun"
TIME_OUT = 10
config.mediaportal.mfmp3_precheck_mp3ids = ConfigYesNo(default = True)
config.mediaportal.mfmp3_discard_mp3_duplicates = ConfigYesNo(default = True)

class show_MFMP3_Genre(MenuHelper):

	ctr = 0
	hash = None
	host = None

	def __init__(self, session, genre_type=('select','',None), genre_title=_('GENRES'), menu_data=None):
		self.__class__.ctr += 1
		self.genre_type = genre_type
		self.genre_title = genre_title
		if genre_type[0] == 'albums':
			skin_name='MP_PluginDescr'
		else:
			skin_name='MP_PluginDescr'

		MenuHelper.__init__(self, session, 0, None, BASE_URL, "", self._defaultlistleft, cookieJar=mfmp3_cookies, skin_name=skin_name)

		self['title'] = Label("MyFreeMP3")
		self['ContentTitle'] = Label(self.genre_title)
		self.menu = menu_data
		self.skipMenuParse = menu_data != None

		self["mfmp3_actions"] = ActionMap(['MP_Actions'], {
			"blue" :  self.blueButton,
			"yellow" :  self.yellowButton,
			"green" :  self.moreButton,
			"nextBouquet" : self.keyPageUp,
			"prevBouquet" : self.keyPageDown
		}, -1)
		self['Page'] = Label("")
		self['F2'] = Label("")
		self['F3'] = Label("")
		self['F4'] = Label("")
		if genre_type[0] == 'albums':
			self['handlung'] = Label()

		self.page = self.pages = 0
		self.nextUrl = self.nextPage = None
		self.yellowButtonTxt = None
		self.moreButtonTxt = None
		self.blueButtonTxt = None
		self.similar = None
		self.genres = None
		self.param_qr = ''
		self.hist_stype = None
		self.hist_menuListe = None
		self.deferredDL = None
		self.title_set = set()
		self.bio_text = ""

		if self.genre_type[0] == 'select':
			self.__class__.ctr = 1
			if config.mediaportal.restorelastservice.value == "1" and not config.mediaportal.backgroundtv.value:
				self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
			else:
				self.lastservice = None
			self.onClose.append(self.restoreLastService)
			self.onClose.append(glob_historyLRUCache.saveCache)
			glob_historyLRUCache.readCache()

		self.onClose.append(self.mfmp3Close)
		self.mh_On_setGenreStrTitle.append((self.showInfos,()))

		self.onLayoutFinish.append(self.mh_start)

	def mh_start(self):
		thread.start_new_thread(self.get_tokens,("GetTokens",))
		self['name'].setText(_("Please wait..."))

	def get_tokens(self, threadName):
		if requestsModule and cfscrapeModule:
			printl("Calling thread: %s" % threadName,self,'A')
			global mfmp3_ck
			global mfmp3_agent
			if mfmp3_ck == {} or mfmp3_agent == '':
				mfmp3_ck, mfmp3_agent = cfscrape.get_tokens(BASE_URL)
				requests.cookies.cookiejar_from_dict(mfmp3_ck, cookiejar=mfmp3_cookies)
			else:
				s = requests.session()
				url = urlparse.urlparse(BASE_URL)
				headers = {'user-agent': mfmp3_agent}
				page = s.get(url.geturl(), cookies=mfmp3_cookies, headers=headers)
				if page.status_code == 503 and page.headers.get("Server") == "cloudflare-nginx":
					mfmp3_ck, mfmp3_agent = cfscrape.get_tokens(BASE_URL)
					requests.cookies.cookiejar_from_dict(mfmp3_ck, cookiejar=mfmp3_cookies)
			reactor.callFromThread(self.mh_initMenu)
		else:
			reactor.callFromThread(self.mh_errorMenu)

	def mh_errorMenu(self):
		message = self.session.open(MessageBoxExt, _("Mandatory depends python-requests and/or python-pyexecjs and nodejs are missing!"), MessageBoxExt.TYPE_ERROR)
		self.keyCancel()

	def parseHash(self, js, err=False):
		if not err:
			try:
				self.__class__.hash = re.search('var hsh="(.*?)"', js).group(1)
			except:
				pass
			else:
				return self.__class__.hash
		printl("Can't parse hash:\n"+str(js),self,'E')

	def mh_initMenu(self):
		self['name'].setText('')
		# temporary fix, no hash available
		self.__class__.hash = "foobar"
		if not self.__class__.hash:
			twAgentGetPage(BASE_URL+'/theme/new/js/lang.js', agent=mfmp3_agent, cookieJar=mfmp3_cookies, timeout=5).addCallback(self.parseHash).addErrback(self.parseHash, True).addCallback(lambda x: self.mh_initMenu())
		else:
			if self.genre_type[0] in ('select','history') or self.skipMenuParse:
				self.mh_menuListe = []
				self.mh_parseCategorys((self.menu,None))
			else:
				if self.genre_type[0] not in ('artists','genres','genresearch') and not self.genre_title.startswith(_('CHARTS')) and not self.genre_title.startswith(_('ALBUM:')):
					historyKey = self.makeHistoryKey(self.genre_title, self.genre_type[0])
					glob_historyLRUCache[historyKey] = (self.genre_title, self.genre_type)

				url = self.genre_type[1]
				if not url.startswith('http'):
					url = self.mh_baseUrl + url
				self.mh_buildMenu(url, True, agent=mfmp3_agent)

	@staticmethod
	def makeHistoryKey(title, genre_type):
		title = title.translate(None,"+- *?_;,()&<>'\"!").lower()
		return "%s-%s" % (title, genre_type)

	def mh_parseCategorys(self, result):
		data, location = result
		if location:
			self.__class__.host = "://".join(http.urlparse(location)[:2])
		if self.skipMenuParse:
			self.mh_genMenu2(data)
			return

		self.menu = []
		dl = []
		if self.genre_type[0] == 'select':
			self.yellowButtonTxt = _("MP3 duplicate check")
			self.blueButtonTxt = _("Precheck MP3-ID's")
			self.menu.append((0, ('mp3search','/mp3/'), _('MP3-SEARCH...')))
			self.menu.append((0, (), _('ARTISTS')))
			self.menu.append((1, ('artists', '/artists/0..9/'), '0..9'))
			for c in map(chr, range(ord('A'), ord('Z')+1)):
				self.menu.append((1, ('artists', '/artists/%s/' % str(c).lower()), c))

			self.menu.append((0, ('charts','/chart/','',''), _('CHARTS')))
			self.menu.append((0, ('genres','/genres/'), _('GENRES')))
			self.menu.append((0, ('history',''), _('SEARCH HISTORY')))
		elif self.genre_type[0] == 'charts':
			self.checkForSimilar(data)
			m = re.search('<ul id="playlist" class="playlist">(.*?)</ul>', data)
			if m:
				self.blueButtonTxt = _("Artist search")
				for me in re.finditer('class="artist">(.*?)</b></a> <a href="(.*?)"> <span class="name">(.*?)</', m.group(1)):
					artist, link, name = me.groups()
					if not link.startswith('http'):
						link = self.mh_baseUrl + link
					img = self.genre_type[2]
					album = self.genre_type[3]
					mentry = (0, (name, album, artist, link, img), '%s - %s' % (artist, name))
					if not config.mediaportal.mfmp3_precheck_mp3ids.value:
						a = mentry[1][2].strip().lower()
						k = self.makeHistoryKey(mentry[1][0], a)
						if not k in self.title_set:
							self.title_set.add(k)
							self.menu.append(mentry)
					else:
						if link.startswith('http://unref.eu'):
							d = defer.Deferred()
							d.callback(mentry)
						else:
							postdata = 'artist=%s&track=%s' % (artist, name)
							d = twAgentGetPage(self.__class__.host+'/song/', method='POST', postdata=postdata, agent=mfmp3_agent, cookieJar=mfmp3_cookies, timeout=5, headers={'Content-Type':'application/x-www-form-urlencoded'})
							d.addCallback(self.getMP3ID, mentry)

						dl.append(d)
		elif self.genre_type[0] == 'genres':
			for m in re.finditer('="artist_list">\s*<li>(.*?)</ul>', data):
				for me in re.finditer('="hash" href="(.*?)">(.*?)</a>', m.group(1)):
					link, name = me.groups()
					self.menu.append((0, ('genreselect', link, name, ''), _('GENRE: ')+name.title()))
			self.blueButtonTxt = _("Genre search")
		elif self.genre_type[0] == 'genresearch':
			m = re.search('="artists_wrap">(.*?)="clear">', data)
			if m:
				for mc in re.finditer('="artist_list">(.*?)</ul>', m.group(1)):
					for me in re.finditer('="hash" href="(.*?)"><li>(.*?)</', mc.group(1)):
						link, name = me.groups()
						self.menu.append((0, ('genreselect', link, name, ''), _('GENRE: ')+name.title()))
		elif self.genre_type[0] == 'artists':
			artistlist_regex = re.compile('class="artist_list">\s*<li>(.*?)</ul>')
			artist_regex = re.compile('="hash" href="(.*?)">(.*?)</a>')
			for m in artistlist_regex.finditer(data):
				for me in artist_regex.finditer(m.group(1)):
					link, artist = me.groups()
					self.menu.append((0, ('listselect', link, artist), artist))
		elif self.genre_type[0] == 'albums':
			self.checkForSimilar(data)
			self.checkForBiotext(data)
			if data and 'id="albums">' in data:
				album_regex = re.compile('<a href="(.*?)" class="hash artwork"><span><img src="(.*?)"></span>(.*?)</')
				title = _('ALBUM: ')
				ltype = 'charts'
			else:
				title = _('ARTIST: ')
				ltype = 'listselect'
				album_regex = re.compile('="hash artwork" href="(.*?)"><span><img src="(.*?)"></span>(.*?)</')

			for m in re.finditer('="albums_covers">\s*<li>(.*?)</ul>', data):
				for me in album_regex.finditer(m.group(1)):
					link, img, album = me.groups()
					self.menu.append((0, (ltype, urllib.quote(link)+'?_pjax=true', img, album), title+album))
		elif self.genre_type[0] in ('songlist','searchlist'):
			self.checkForSimilar(data)
			self.checkForGenres(data)

			if self.genre_type[0] == "searchlist" and data and '="button hash">More</' in data:
				self.moreButtonTxt = _("More")
			else:
				self.moreButtonTxt = ""

			m = re.search('class="playlist">(.*?)</ul>', data)
			if m:
				self.blueButtonTxt = _("Artist search")
				if 'window.open(' in m.group(1):
					regex = 'window\.open\(\'(.*?)\'.*?="artist">(.*?)<.*?="name">(.*?)<'
				else:
					regex = '="(artist)">(.*?)<.*?="name">(.*?)<'

				for me in re.finditer(regex, m.group(1)):
					link, artist, name = me.groups()
					album = ''
					mentry = (0, (name, album, artist, link, ''), '%s - %s' % (artist, name))
					if not config.mediaportal.mfmp3_precheck_mp3ids.value:
						a = mentry[1][2].strip().lower()
						k = self.makeHistoryKey(mentry[1][0], a)
						if not k in self.title_set:
							self.title_set.add(k)
							self.menu.append(mentry)
					else:
						if link.startswith('http://unref.eu'):
							d = defer.Deferred()
							d.callback(mentry)
						else:
							postdata = 'artist=%s&track=%s' % (artist, name)
							d = twAgentGetPage(self.__class__.host+'/song/', method='POST', postdata=postdata, agent=mfmp3_agent, cookieJar=mfmp3_cookies, timeout=5, headers={'Content-Type':'application/x-www-form-urlencoded'})
							d.addCallback(self.getMP3ID, mentry)

						dl.append(d)
		elif self.genre_type[0] == 'history':
			if self.hist_menuListe:
				self.hist_menuListe = None
				self.mh_menuListe = []
				for key, val in glob_historyLRUCache.cache:
					genre_title, genre_type = val
					self.mh_menuListe.append((genre_title, genre_type + (key,)))

				stype = self.hist_stype
				self.hist_stype = ''
				return self.cb_handleHistoryOrder((None, stype))
			else:
				for key, val in glob_historyLRUCache.cache:
					genre_title, genre_type = val
					self.menu.insert(0,(0, genre_type + (key,), genre_title))

				self.hist_stype = 'all'
				self.yellowButtonTxt = _("Delete")
				self.moreButtonTxt = _("Select Order")

		self.nextUrl, self.nextPage = self.getPagination(data)
		if not dl:
			self.mh_genMenu2(self.menu)
		else:
			self.ml.setList(map(self.mh_menuListentry, [(_("Get Song ID's..."),None)]))
			self.onClose.append(self.cancelDL)
			self.deferredDL = defer.DeferredList(dl, consumeErrors=True)
			self.deferredDL.addCallback(self.gotMP3_results)

	def checkForSimilar(self, data):
		if data and 'class="similar_cont"><ul>' in data and self.__class__.ctr < 10:
			m = re.search('class="similar_cont"><ul>(.*?)</ul>', data)
			self.similar = []
			for sa in re.finditer('="hash" href="(.*?)"><li>(.*?)</', m.group(1)):
				link, name = sa.groups()
				self.similar.append((0, ('genreselect', link, name), name.title()))

			if self.similar:
				self.yellowButtonTxt = _("Similar genres")
			else:
				self.yellowButtonTxt = ""
		elif data and not self.similar and '="playlist radio_list">' in data and self.__class__.ctr < 10:
			m = re.search('="playlist radio_list">(.*?)</ul>', data)
			self.similar = []
			for sa in re.finditer('="radio_logo">.*?<a href="(.*?)".*?="hash">(.*?)</', m.group(1)):
				link, artist = sa.groups()
				self.similar.append((0, ('listselect', link, artist), artist))

			if self.similar:
				self.yellowButtonTxt = _("Similar artists")
			else:
				self.yellowButtonTxt = ""
		elif data and not self.similar and '<a href="#">Simlar artists</a>' in data and self.__class__.ctr < 10:
			m = re.search('<a href="#">Simlar artists</a>(.*?)class="clear">', data)
			self.similar = []
			for sa in re.finditer('="hash tag" href="(.*?)"><span>(.*?)</', m.group(1)):
				link, artist = sa.groups()
				self.similar.append((0, ('listselect', link, artist), artist))

			if self.similar:
				self.yellowButtonTxt = _("Similar artists")
			else:
				self.yellowButtonTxt = ""

	def checkForBiotext(self, data):
		if self.genre_type[0] == 'albums' and '="artist_bio text">' in data:
			m = re.search('="artist_bio text">(.*?)</div', data)
			if m:
				self.bio_text = decodeHtml(m.group(1).strip())
				self.bio_text = re.sub('  \s+', '\n', self.bio_text)

	def checkForGenres(self, data):
		if data and '<a href="#">Genres</a>' in data and self.__class__.ctr < 10:
			m = re.search('<a href="#">Genres</a>(.*?)class="clear">', data)
			self.genres = []
			for sa in re.finditer('="hash tag" href="(.*?)"><span>(.*?)</', m.group(1)):
				link, name = sa.groups()
				self.genres.append((0, ('genreartists', link, name), _('GENRE: ')+name.title()))

			if self.genres:
				self.blueButtonTxt = _("Genres")
			else:
				self.blueButtonTxt = ""

	def mh_callGenreListScreen(self):
		self.menu = None
		if self.genre_type[0] in ('select', 'genres', 'artists', 'albums', 'genreselect', 'genresearch', 'history'):
			if self.mh_genreUrl[self.mh_menuLevel][0] == 'listselect':
				self.handleListSel()
			elif self.mh_genreUrl[self.mh_menuLevel][0] in ('mp3search','genresearch'):
				self.searchQuery()
			elif self.mh_genreUrl[self.mh_menuLevel][0] == 'genreselect':
				self.handleGenreSel()
			elif self.mh_genreUrl[self.mh_menuLevel][0] == 'genreartists':
				genre_title = _('ARTISTS: %s') % self.mh_genreUrl[self.mh_menuLevel][2].strip().title()
				genre_type = ('albums',) + self.mh_genreUrl[self.mh_menuLevel][1:]
				self.session.open(show_MFMP3_Genre, genre_type=genre_type, genre_title=genre_title)
			elif self.genre_type[0] == 'history':
				self.session.openWithCallback(self.mh_initMenu, show_MFMP3_Genre, genre_type=self.mh_genreUrl[self.mh_menuLevel], genre_title=self.mh_genreTitle)
			else:
				self.session.open(show_MFMP3_Genre, genre_type=self.mh_genreUrl[self.mh_menuLevel], genre_title=self.mh_genreTitle)
		elif self.genre_type[0] in ('charts', 'songlist', 'searchlist'):
			idx = self['liste'].getSelectedIndex()
			img = self.mh_menuListe[idx][1][4]
			if img and len(img) > 4 and img[-4] == '.':
				cover = img.split('.')[-1] in ('png','jpg','gif')
			else:
				cover = False
			self.session.open(
				MFMP3_Player,
				self.__class__.host,
				self.__class__.hash,
				self.mh_menuListe,
				idx,
				listTitle = self.genre_title,
				cover=cover
				)

	def handleGenreSel(self):
		list = (
				( _('TOP TRACKS'), 'charts'),
				( _('ARTISTS'), 'albums')
			)

		self.session.openWithCallback(self.cb_handleGenreSel, ChoiceBoxExt, title=_("List Selection"), list = list)

	def cb_handleGenreSel(self, answer):
		ltype = answer and answer[1]
		if ltype:
			link = self.mh_genreUrl[self.mh_menuLevel][1]
			link = link.replace('+', '%20')
			genre = self.mh_genreUrl[self.mh_menuLevel][2]
			genre_title = '%s: %s' % (answer[0], genre.strip().title())
			if ltype == "albums":
				link = link.replace('/tag/track', '/tag/artist')
			else:
				link = link.replace('/tag/artist', '/tag/track')

			self.session.open(show_MFMP3_Genre, genre_type=(ltype, link, genre, ''), genre_title=genre_title)

	def handleListSel(self):
		list = (
				( _('ALBUMS'), 'albums'),
				( _('TOP TRACKS'), 'charts'),
				( _('ALL TRACKS'), 'songlist')
			)

		self.session.openWithCallback(self.cb_handleListSel, ChoiceBoxExt, title=_("List Selection"), list = list)

	def cb_handleListSel(self, answer):
		ltype = answer and answer[1]
		if ltype:
			if self.moreButtonTxt:
				link = self.genre_type[1]
				artist = urllib.unquote_plus(link.split('/')[-1])
			else:
				link = self.mh_genreUrl[self.mh_menuLevel][1]
				artist = self.mh_genreUrl[self.mh_menuLevel][-1]

			genre_title = '%s: %s' % (answer[0], artist.strip().title())
			if ltype == "albums":
				link = link.replace('/mp3','/artist')
				self.session.open(show_MFMP3_Genre, genre_type=(ltype, link), genre_title=genre_title)
			elif ltype == "charts":
				link = link.replace('/mp3','/artist')
				self.session.open(show_MFMP3_Genre, genre_type=(ltype, link, '', ''), genre_title=genre_title)
			elif  ltype == "songlist":
				link = link.replace('/artist','/mp3')
				if self.moreButtonTxt:
					self['ContentTitle'].setText(genre_title)
				else:
					self.session.open(show_MFMP3_Genre, genre_type=(ltype, link), genre_title=genre_title)

	def handleHistoryOrder(self):
		list = (
				( _('Show only MP3-SEARCH'), _('MP3-SEARCH')),
				( _('Show only ALBUMS'), _('ALBUMS')),
				( _('Show only ARTISTS'), _('ARTISTS')),
				( _('Show only TOP TRACKS'), _('TOP TRACKS')),
				( _('Show only ALL TRACKS'), _('ALL TRACKS')),
				( _('Show All'), 'all')
			)

		sel = 0
		if not self.hist_stype: self.hist_stype = 'all'
		for me in list:
			if me[1] == self.hist_stype: break
			sel += 1

		self.session.openWithCallback(self.cb_handleHistoryOrder, ChoiceBoxExt, title=_("List Selection"), list = list, selection=sel)

	def cb_handleHistoryOrder(self, answer):
		stype = answer and answer[1]
		if stype and self.hist_stype != stype:
			self.hist_stype = stype
			if not self.hist_menuListe:
				self.hist_menuListe = self.mh_menuListe

			if stype != 'all':
				self.mh_menuListe = []
				for name, url in self.hist_menuListe:
					if stype in name:
						self.mh_menuListe.append((name,url))
			else:
				self.mh_menuListe = self.hist_menuListe

			if not self.mh_menuListe:
				self.ml.setList(map(self.mh_menuListentry, [(_('No results found!'),None)]))
			else:
				self.mh_menuListe.sort(key=lambda t : t[0].lower())
				self.ml.setList(map(self.mh_menuListentry, self.mh_menuListe))
				self.mh_menuIdx[0] = 0
				self['liste'].moveToIndex(self.mh_menuIdx[0])
			self.mh_setGenreStrTitle()

	def setCheck(self, callback, conf_val, title):
		list = (
				( _('Yes'), "1"),
				( _('No'), "0")
			)

		if conf_val:
			yesno = _("Yes")
			sel = 0
		else:
			yesno = _("No")
			sel = 1

		self.session.openWithCallback(callback, ChoiceBoxExt, title=title + yesno, list = list, selection=sel)

	def cb_setPrecheckMP3(self, answer):
		stype = answer and answer[1]
		if stype:
			if stype == "1":
				config.mediaportal.mfmp3_precheck_mp3ids.value = True
			else:
				config.mediaportal.mfmp3_precheck_mp3ids.value = False

			config.mediaportal.mfmp3_precheck_mp3ids.save()

	def cb_setCheckDuplicates(self, answer):
		stype = answer and answer[1]
		if stype:
			if stype == "1":
				config.mediaportal.mfmp3_discard_mp3_duplicates.value = True
			else:
				config.mediaportal.mfmp3_discard_mp3_duplicates.value = False

			config.mediaportal.mfmp3_discard_mp3_duplicates.save()

	def showInfos(self):
		if self.page:
			page = str(self.page)
			if self.pages:
				page += ' / %d' % self.pages
			elif self.page:
				if not self.nextPage:
					self.pages = self.page
					page += ' / %d' % self.pages
				else:
					page += ' / +'
			self['Page'].setText(_("Page:"))
			self['page'].setText(page)

		if self.blueButtonTxt:
			self['F4'].setText(self.blueButtonTxt)
		else:
			self['F4'].setText('')

		if self.yellowButtonTxt:
			self['F3'].setText(self.yellowButtonTxt)
		else:
			self['F3'].setText('')

		if self.moreButtonTxt:
			self['F2'].setText(self.moreButtonTxt)
		else:
			self['F2'].setText('')

		if self.genre_type[0] == 'albums':
			self['handlung'].setText(self.bio_text)
			try:
				CoverHelper(self['coverArt']).getCover(self.mh_genreUrl[self.mh_menuLevel][2], agent=mfmp3_agent, cookieJar=mfmp3_cookies)
			except:
				pass

	def getPagination(self, data):
		href = page = None
		if data and '="pagination">' in data:
			m = re.search('class="pagination"><a href="(.*?\?page=)(\d+)', data)
			if m:
				href, page = m.groups()
				href = '%s%s' % (self.__class__.host, href)
				page = int(page)
				self.page = page - 1
		elif self.page and not self.pages:
			self.pages = self.page

		return (href, page)

	def searchQuery(self):
		self.session.openWithCallback(self.cb_searchQuery, VirtualKeyBoardExt, title = (_("Enter search criteria")), text = self.param_qr, is_dialog=True)

	def cb_searchQuery(self, callback = None, entry = None):
		if callback != None:
			self.param_qr = callback.strip().title()
			qr = urllib.quote_plus(self.param_qr)
			if self.genre_type[0] in ('genres','genresearch'):
				url = '%s%s/' % (self.genre_type[1], qr)
				genre_title = '%s: %s' % (_('GENRE-SEARCH'), self.param_qr)
				genre_type = ('genresearch', url)
			elif self.blueButtonTxt == _('Artist search'):
				url = '/mp3/' + qr
				genre_title = '%s: %s' % (_('MP3-SEARCH'), self.param_qr)
				genre_type = ('searchlist', url)
			else:
				url = self.mh_genreUrl[self.mh_menuLevel][1] + qr
				genre_title = '%s: %s' % (_('MP3-SEARCH'), self.param_qr)
				genre_type = ('searchlist', url)

			self.session.open(show_MFMP3_Genre, genre_type=genre_type, genre_title=genre_title)

	def getMP3ID(self, data, mentry):
		if data:
			m = re.search('"duration_min":"(.*?)","ownerid_aid":"(.*?)"', data)
			if m:
				dura, id = m and m.groups()
				if id != '_':
					link = 'http://www.myfreemp3.eu/play/%s_%s/' % (id, self.hash)
					mentry = (mentry[0], mentry[1][:3]+(link,)+mentry[1][4:], mentry[2])
					return mentry

		raise Exception('getMP3ID')

	def gotMP3_results(self, res):
		for entry in res:
			if entry[0]:
				if config.mediaportal.mfmp3_discard_mp3_duplicates.value:
					a = entry[1][1][2].strip().lower()
					k = self.makeHistoryKey(entry[1][1][0], a)
					if not k in self.title_set:
						self.title_set.add(k)
						self.menu.append(entry[1])
				else: self.menu.append(entry[1])

		self.deferredDL = None
		self.title_set.clear()
		self.mh_genMenu2(self.menu)

	def cancelDL(self):
		if self.deferredDL:
			self.deferredDL.cancel()

	def keyPageUp(self):
		if self.mh_keyLocked or not self.nextPage:
			return

		oldpage = self.page
		self.page = self.nextPage
		if oldpage != self.page:
			self.loadNextPage(self.page)

	def keyPageDown(self):
		if self.mh_keyLocked or not self.page > 1:
			return

		oldpage = self.page
		self.page -= 1
		if oldpage != self.page:
			self.loadNextPage(self.page)

	def loadNextPage(self, page):
		self.mh_keyLocked = True
		url = self.nextUrl + str(page)
		self.genre_type = (self.genre_type[0], url)
		self.mh_initMenu()

	def yellowButton(self):
		if self.mh_keyLocked or not self.yellowButtonTxt:
			return
		self.menu = None
		if self.genre_type[0] == 'history':
			key = self.mh_genreUrl[self.mh_menuLevel][-1]
			del glob_historyLRUCache[key]
			self.mh_initMenu()
		elif self.genre_type[0] == 'select':
			self.setCheck(self.cb_setCheckDuplicates, config.mediaportal.mfmp3_discard_mp3_duplicates.value, _("Discard MP3 Duplicate's: "))
		else:
			if _("Similar artists") == self.yellowButtonTxt:
				title = _('SIMILAR ARTISTS')
			else:
				title = _('SIMILAR GENRES')

			genre_type = ('genres',) + self.mh_genreUrl[self.mh_menuLevel][1:]
			self.session.open(show_MFMP3_Genre, genre_type=genre_type, genre_title=title, menu_data=self.similar)

	def blueButton(self):
		if self.mh_keyLocked or not self.blueButtonTxt:
			return
		self.menu = None
		if self.genre_type[0] == 'genres':
			self.searchQuery()
		elif self.genre_type[0] == 'select':
			self.setCheck(self.cb_setPrecheckMP3, config.mediaportal.mfmp3_precheck_mp3ids.value, _("Precheck MP3-ID's: "))
		elif self.blueButtonTxt == _('Artist search'):
			self.param_qr = self.mh_genreUrl[self.mh_menuLevel][2]
			self.searchQuery()
		else:
			genre_type = ('genreselect','',None)
			self.session.open(show_MFMP3_Genre, genre_type=genre_type, menu_data=self.genres)

	def moreButton(self):
		if self.mh_keyLocked or not self.moreButtonTxt:
			return

		if self.genre_type[0] == 'history':
			self.handleHistoryOrder()
		elif self.genre_type[0] == 'genres':
			self.handleGenreSel()
		else:
			self.handleListSel()

	def restoreLastService(self):
		if config.mediaportal.restorelastservice.value == "1" and not config.mediaportal.backgroundtv.value:
			self.session.nav.playService(self.lastservice)
		else:
			self.session.nav.stopService()

	def mfmp3Close(self):
		self.__class__.ctr -= 1

class MFMP3_Player(SimplePlayer):

	def __init__(self, session, host, hash, playList, playIdx, listTitle,cover):
		SimplePlayer.__init__(self, session, playList, playIdx=playIdx, playAll=True, listTitle=listTitle, ltype='myfreemp3', autoScrSaver=True, cover=cover, playerMode='MP3', googleCoverSupp=True, embeddedCoverArt=True)
		self.mfmp3_playIdx = 0
		self._host = host
		self._hash = hash
		self.tw_agent_hlp = TwAgentHelper(followRedirect=True)

	def getVideo(self):
		self.mfmp3_playIdx = self.playIdx
		url = self.playList[self.mfmp3_playIdx][1][3]
		if url == '_skip_':
			self.dataError(_('No MP3-Id found: Skip:\n') + self.playList[self.mfmp3_playIdx][1][0])
		elif url.startswith('http://www.my-free-mp3.org') or url.startswith('http://unref.eu'):
			if url.startswith('http://unref.eu'):
				twAgentGetPage(url, timeout=TIME_OUT).addCallback(self.getV3).addErrback(self.getV3, True)
			else:
				self.getMP3(url)
		else:
			data = 'artist=%s&track=%s' % (self.playList[self.mfmp3_playIdx][1][2], self.playList[self.mfmp3_playIdx][1][0])
			twAgentGetPage(self._host+'/song/', method='POST', postdata=data, agent=mfmp3_agent, cookieJar=mfmp3_cookies, timeout=TIME_OUT, headers={'Content-Type':'application/x-www-form-urlencoded'}).addCallback(self.getV2).addErrback(self.getV2, True)

	def getV2(self, data, err=False):
		id = '_'
		if not err and data:
			m = re.search('"duration_min":"(.*?)","ownerid_aid":"(.*?)"', data)
			if m:
				dura, id = m and m.groups()
				if id != '_':
					link = 'http://www.my-free-mp3.org/play/%s_%s/' % (id, self._hash)
					entry = self.playList[self.mfmp3_playIdx]
					if not entry[1][3].startswith('http://www.my-free-mp3.org'):
						entry = (entry[0], entry[1][:3]+(link,)+entry[1][4:])
						self.playList[self.mfmp3_playIdx] = entry
					self.getMP3(link)

		if id == '_':
			entry = self.playList[self.mfmp3_playIdx]
			entry = (entry[0], entry[1][:3]+('_skip_',)+entry[1][4:])
			self.playList[self.mfmp3_playIdx] = entry
			self.dataError(_('No MP3-Id found:\n') + self.playList[self.mfmp3_playIdx][1][0])

	def getV3(self, data, err=False):
		if not err:
			m = re.search('window.open\("(.*?)"', data)
			if m:
				url = m.group(1)
				return self.getMP3(url)
		self.dataError(_('No MP3-Stream found:\n') + self.playList[self.playIdx][1][0])

	def getMP3(self, url):
		file = re.findall('play\/([0-9a-z\_]+)', url, re.S)
		playurl = "http://mp3mp3.site/stream.php?q=%s_/" % file[0]
		title = decodeHtml(self.playList[self.mfmp3_playIdx][1][0])
		album = decodeHtml(self.playList[self.mfmp3_playIdx][1][1])
		artist = decodeHtml(self.playList[self.mfmp3_playIdx][1][2])
		img = self.playList[self.mfmp3_playIdx][1][4]
		self.playStream(title, playurl, album=album, artist=artist, imgurl=img)