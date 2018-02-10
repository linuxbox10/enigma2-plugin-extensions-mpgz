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

from update import *

config.mpgz = ConfigSubsection()
config.mpgz.version = NoSave(ConfigText(default="2018020801"))

def autostart(reason, session=None, **kwargs):
	if reason == 0:
		if session is not None:
			_session = session
			addFont(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaPortal/resources/") + "mediaportal1.ttf", "mediaportal", 100, False)
			addFont(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaPortal/resources/") + "mediaportal_clean.ttf", "mediaportal_clean", 100, False)
			if config.mediaportal.autoupdate.value:
				config.misc.standbyCounter.addNotifier(checkupdate(session).standbyCounterChanged, initial_call = False)
				checkupdate(session).checkforupdate()

def Plugins(path, **kwargs):
	result = [
		PluginDescriptor(name="mpgz", description="mpgz - Updater", where = [PluginDescriptor.WHERE_AUTOSTART, PluginDescriptor.WHERE_SESSIONSTART], fnc = autostart, wakeupfnc = None)
	]
	return result