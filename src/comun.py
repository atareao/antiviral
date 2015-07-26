#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# comun.py
#
# Copyright (C) 2011,2012 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#

__author__ = 'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'
__date__ ='$05/08/2012$'
__copyright__ = 'Copyright (c) 2012 Lorenzo Carbonell'
__license__ = 'GPLV3'
__url__ = 'http://www.atareao.es'

import sys
import os
import locale
import gettext
######################################

def is_package():
    return __file__.find('src') < 0

######################################

PARAMS = {	'first-time':True,
			'version':'',
			'folders':[],
			'infected':[]
			}



APP = 'antiviral'
ICONNAME = 'antiviral.svg'
#########################################
APPNAME = APP.title()
APP_CONF = APP + '.conf'
CONFIG_DIR = os.path.join(os.path.expanduser('~'),'.config')
CONFIG_APP_DIR = os.path.join(CONFIG_DIR, APP)
QUARENTINE_DIR = os.path.join(CONFIG_APP_DIR, '.quarentine')
CONFIG_FILE = os.path.join(CONFIG_APP_DIR, APP_CONF)

# check if running from source
if is_package():
    ROOTDIR = '/opt/extras.ubuntu.com/antiviral/share/'
    LANGDIR = os.path.join(ROOTDIR, 'locale-langpack')
    APPDIR = os.path.join(ROOTDIR, APP)
    ICON = os.path.join('/opt/extras.ubuntu.com/antiviral/share/pixmaps',ICONNAME)
    CHANGELOG = os.path.join(APPDIR,'changelog')
else:
    ROOTDIR = os.path.dirname(__file__)
    LANGDIR = os.path.normpath(os.path.join(ROOTDIR, '../template1'))
    DATADIR = os.path.normpath(os.path.join(ROOTDIR, '../data'))
    ICON = os.path.join(DATADIR,ICONNAME)
    APPDIR = ROOTDIR
    DEBIANDIR = os.path.normpath(os.path.join(ROOTDIR, '../debian'))
    CHANGELOG = os.path.join(DEBIANDIR,'changelog')

f = open(CHANGELOG,'r')
line = f.readline()
f.close()
pos=line.find('(')
posf=line.find('-',pos)
VERSION = line[pos+1:posf].strip()
if not is_package():
	VERSION = VERSION + '-src'

try:
	current_locale, encoding = locale.getdefaultlocale()
	language = gettext.translation(APP, LANGDIR, [current_locale])
	language.install()
	print(language)
	if sys.version_info[0] == 3:
		_ = language.gettext
	else:
		_ = language.ugettext
except Exception as e:
	print(e)
	_ = str
