#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#       antiviral.py
#       
#       Copyright 2010 Lorenzo Carbonell <atareao@zorita>
#       
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.

import gi  
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Nautilus
from gi.repository import GObject
import os
import sys
import urllib
if __file__.startswith('/usr/share/nautilus-python/extensions') or os.getcwd().startswith('/usr/share/nautilus-python/extensions'):
	sys.path.insert(1, '/opt/extras.ubuntu.com/antiviral/share/antiviral')
from antiviral import Antiviral
from comun import _

def get_files(files_in):
	files = []
	for file_in in files_in:
		print(file_in)
		file_in = urllib.unquote(file_in.get_uri()[7:])
		print(file_in)
		if os.path.isdir(file_in):
			files.append(file_in)
	return files

########################################################################

"""
Antiviral menu
"""	
class AntiviralMenuProvider(GObject.GObject, Nautilus.MenuProvider):
	"""Implements the 'Replace in Filenames' extension to the nautilus right-click menu"""

	def __init__(self):
		"""Nautilus crashes if a plugin doesn't implement the __init__ method"""
		pass
		
	def get_file_items(self, window, sel_items):
		"""Adds the 'Replace in Filenames' menu item to the Nautilus right-click menu,
		   connects its 'activate' signal to the 'run' method passing the selected Directory/File"""
		sel_items = get_files(sel_items)
		if not len(sel_items)>0:
			return
		item = Nautilus.MenuItem(name='AntiviralMenuProvider::Gtk-pdf-tools',
								 label=_('Scan folder'),
								 tip=_('Scan this folder'),
								 icon='Gtk-find-and-replace')
		item.connect('activate', self.addfolders, sel_items)
		return item,
		#
	def addfolders(self,menu,selected):
		av=Antiviral(from_nautilus=True,folders=selected)
		av.run()
		av.destroy()

if __name__ == '__main__':
	av=Antiviral()
	Gtk.main()
	

