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
import Plugins.Extensions.MediaPortal.resources.mp_globals
from Plugins.Extensions.MediaPortal.resources.messageboxext import MessageBoxExt
from Plugins.Extensions.MediaPortal.resources.twagenthelper import twAgentGetPage
import random
gLogFile = None

class checkupdate:

	def __init__(self, session):
		self.session = session
		mp_globals.currentskin = config.mediaportal.skin2.value

	def standbyCounterChanged(self, configElement):
		from Screens.Standby import inStandby
		inStandby.onClose.append(self.leaveStandby)

	def leaveStandby(self):
		self.checkforupdate()

	def checkforupdate(self):
		update_agent = getUserAgent()
		update_url = "http://feed.newnigma2.to/mpgz/version.txt"
		twAgentGetPage(update_url, agent=update_agent, timeout=60).addCallback(self.gotUpdateInfo).addErrback(self.gotError)

	def gotError(self, error=""):
		printl(error,self,"E")
		return

	def gotUpdateInfo(self, html):
		if re.search(".*?<html", html):
			return
		self.html = html
		tmp_infolines = html.splitlines()
		remoteversion_ipk = re.sub('\D', '', tmp_infolines[0])
		remoteversion_deb = re.sub('\D', '', tmp_infolines[2])
		remote_mp_version = re.sub('\D', '', tmp_infolines[4])
		if mp_globals.isDreamOS:
			self.updateurl = tmp_infolines[3]
			remoteversion = remoteversion_deb
		else:
			self.updateurl = tmp_infolines[1]
			remoteversion = remoteversion_ipk

		if int(config.mpgz.version.value) < int(remoteversion) and int(config.mediaportal.version.value) >= int(remote_mp_version):
			self.session.openWithCallback(self.startUpdate,MessageBoxExt,_("An update is available for the %s Plugin!\nDo you want to download and install it now?" % "mpgz"), MessageBoxExt.TYPE_YESNO, timeout=15, default=False)
			return
		else:
			return

	def startUpdate(self,answer):
		if answer is True:
			self.session.open(MPUpdateScreen,self.updateurl)
		else:
			return

class MPUpdateScreen(Screen):

	def __init__(self, session, updateurl):
		self.session = session
		self.updateurl = updateurl

		self.skin_path = mp_globals.pluginPath + mp_globals.skinsPath
		path = "%s/%s/MP_Update.xml" % (self.skin_path, mp_globals.currentskin)
		if not fileExists(path):
			path = self.skin_path + mp_globals.skinFallback + "/MP_Update.xml"
		with open(path, "r") as f:
			self.skin = f.read()
			f.close()

		self.ml = MenuList([])
		self['mplog'] = self.ml
		self.list = []

		Screen.__init__(self, session)
		self['title'] = Label("mpgz Update")
		self.setTitle("mpgz Update")

		self.onLayoutFinish.append(self.__onLayoutFinished)

	def __onLayoutFinished(self):
		height = self['mplog'].l.getItemSize().height()
		try:
			self.ml.l.setFont(gFont("mediaportal", height - 2 * mp_globals.sizefactor))
		except:
			pass
		self.list.append(_("Starting update, please wait..."))
		self.ml.setList(self.list)
		self.ml.moveToIndex(len(self.list)-1)
		self.ml.selectionEnabled(False)
		self.startPluginUpdate()

	def startPluginUpdate(self):
		self.container=eConsoleAppContainer()
		if mp_globals.isDreamOS:
			self.container.appClosed_conn = self.container.appClosed.connect(self.finishedPluginUpdate)
			self.container.stdoutAvail_conn = self.container.stdoutAvail.connect(self.mplog)
			self.container.execute("apt-get update ; wget -q -O /tmp/foobar %s ; dpkg --install --force-overwrite /tmp/foobar ; apt-get -y -f install" % str(self.updateurl))
		else:
			self.container.appClosed.append(self.finishedPluginUpdate)
			self.container.stdoutAvail.append(self.mplog)
			self.container.execute("opkg update ; opkg install --force-overwrite " + str(self.updateurl))

	def finishedPluginUpdate(self,retval):
		self.container.kill()
		if retval == 0:
			config.mediaportal.filter.value = "ALL"
			config.mediaportal.filter.save()
			configfile.save()
			self.session.openWithCallback(self.restartGUI, MessageBoxExt, _("%s successfully updated!\nDo you want to restart the Enigma2 GUI now?" % "mpgz"), MessageBoxExt.TYPE_YESNO)
		else:
			self.session.openWithCallback(self.returnGUI, MessageBoxExt, _("%s update failed! Check the update log carefully!" % "mpgz"), MessageBoxExt.TYPE_ERROR)

	def restartGUI(self, answer):
		if answer is True:
			self.session.open(TryQuitMainloop, 3)
		self.close()

	def returnGUI(self, answer):
		self.close()

	def mplog(self,str):
		self.list.append(str)
		self.ml.setList(self.list)
		self.ml.moveToIndex(len(self.list)-1)
		self.ml.selectionEnabled(False)
		self.writeToLog(str)

	def writeToLog(self, log):
		global gLogFile

		if gLogFile is None:
			self.openLogFile()

		now = datetime.datetime.now()
		gLogFile.write(str(log) + "\n")
		gLogFile.flush()

	def openLogFile(self):
		global gLogFile
		baseDir = "/tmp"
		logDir = baseDir + "/mpgz"

		now = datetime.datetime.now()

		try:
			os.makedirs(baseDir)
		except OSError, e:
			pass

		try:
			os.makedirs(logDir)
		except OSError, e:
			pass

		gLogFile = open(logDir + "/mpgz_update_%04d%02d%02d_%02d%02d.log" % (now.year, now.month, now.day, now.hour, now.minute, ), "w")