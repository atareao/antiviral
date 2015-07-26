#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#       acciones.py
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
import comun
import os
import shutil
from configurator import Configuration
from comun import _

class Actions(Gtk.Dialog):
	def __init__(self,parent=None,infectados=None):
		Gtk.Dialog.__init__(self,comun.APPNAME,parent,Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,(Gtk.STOCK_CLOSE, Gtk.ResponseType.ACCEPT))		
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_title(comun.APP)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.on_close_application)		
		self.infectados=infectados
		#
		#
		vbox = Gtk.VBox(spacing = 5)
		vbox.set_border_width(5)
		self.get_content_area().add(vbox)
		#
		frame1 = Gtk.Frame()
		vbox.pack_start(frame1,True,True,0)
		vbox1 = Gtk.VBox(spacing = 5)
		vbox1.set_border_width(5)
		frame1.add(vbox1)

		hbox1 = Gtk.HBox(spacing = 5)
		hbox1.set_border_width(5)
		vbox1.pack_start(hbox1,True,True,0)
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
		scrolledwindow.set_size_request(650, 400)		
		hbox1.pack_start(scrolledwindow,True,True,0)		
		model = Gtk.ListStore(bool,bool,str,str)
		self.treeview = Gtk.TreeView(model)
		scrolledwindow.add(self.treeview)
		crt0 = Gtk.CellRendererToggle()
		crt0.set_property('activatable',True)
		column0 = Gtk.TreeViewColumn(_('Del.'),crt0,active=0)
		crt0.connect("toggled", self.toggled_cb, (model, 0))
		self.treeview.append_column(column0)
		crt1 = Gtk.CellRendererToggle()
		crt1.set_property('activatable',True)
		column1 = Gtk.TreeViewColumn(_('Qua.'),crt1,active=1)
		crt1.connect("toggled", self.toggled_cb, (model, 1))
		self.treeview.append_column(column1)
		#
		column = Gtk.TreeViewColumn(_('File'),Gtk.CellRendererText(),text=2)
		self.treeview.append_column(column)		
		column = Gtk.TreeViewColumn(_('Virus'),Gtk.CellRendererText(),text=3)
		self.treeview.append_column(column)		
		#
		vbox1 = Gtk.VBox()
		hbox1.pack_end(vbox1,False,False,0)
		button1 = Gtk.Button()
		button1.set_size_request(40,40)
		button1.set_tooltip_text(_('Execute'))	
		button1.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_EXECUTE,Gtk.IconSize.BUTTON))
		button1.connect('clicked',self.on_button1_clicked)		
		vbox1.pack_start(button1,False,False,0)		
		#
		if infectados:
			for infectado in self.infectados:
				model.append([False,False,infectado['file'],infectado['virus']])
		self.show_all()

	def toggled_cb(self,cell, path, user_data):
		model, column = user_data		
		old_value = model[path][column]
		new_value = not old_value
		model[path][column] = new_value
		if new_value:
			if column == 1:
				model[path][0] = False
			elif column == 0:
				model[path][1] = False
		return

	def on_button1_clicked(self,widget):
		iters_removed = []
		infected = []
		model = self.treeview.get_model()
		itera=model.get_iter_first()
		if not os.path.exists(comun.QUARENTINE_DIR):
			os.mkdir(comun.QUARENTINE_DIR)
		while(itera!=None):
			delete = model.get(itera, 0)[0]
			quarentine = model.get(itera, 1)[0]			
			filename=model.get(itera, 2)[0]
			virus=model.get(itera, 3)[0]
			if delete:
				if os.path.exists(filename):
					os.remove(filename)
				iters_removed.append(itera)
			elif quarentine:
				if os.path.exists(filename):					
					try:
						shutil.move(filename,comun.QUARENTINE_DIR)
						infected_file = {'file':filename,'virus':virus}
						infected.append(infected_file)
					except shutil.Error:
						md = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
						Gtk.ButtonsType.YES_NO,
						_('There is a file like this in quarentine, remove this new file?'))
						md.set_title('Antiviral')
						if md.run() == Gtk.ResponseType.YES:
							os.remove(filename)
							infected_file = {'file':filename,'virus':virus}
							infected.append(infected_file)
						md.destroy()			
						
				iters_removed.append(itera)
			itera=model.iter_next(itera)
		for iter_removed in iters_removed:
			model.remove(iter_removed)
		if infected and len(infected)>0:
			configuration = Configuration()
			configuration.set('infected',infected)
			configuration.save()
		
	def on_close_application(self,widget):
		self.hide()
if __name__ == '__main__':
	infectado = {'file':'/home/atareao/test/testtte.txt','virus':'avirus'}
	infectados = []
	infectados.append(infectado)
	actions=Actions(infectados = infectados)
	actions.run()

