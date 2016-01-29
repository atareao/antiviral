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
from gi.repository import GdkPixbuf
import os
import pyclamd
import subprocess
import comun
from configurator import Configuration
from actions import Actions
from progreso import Progreso
from comun import _

class Antiviral(Gtk.Dialog):
	
	def __init__(self,from_nautilus=False,folders=[]):
		Gtk.Dialog.__init__(self)
		self.set_title('antiviral')
		self.set_modal(True)
		self.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
		#
		try:
			self.scanner = pyclamd.ClamdUnixSocket()
			self.scanner.ping()
		except pyclamd.ConnectionError:
			self.scanner = pyclamd.ClamdNetworkSocket()
			try:
				self.scanner.ping()
			except pyclamd.ConnectionError:
					exit(0)		
		#print(self.scanner.reload())
		print(self.scanner.stats())
		#
		self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
		self.set_title(comun.APP)
		self.set_default_size(750, 600)
		self.set_icon_from_file(comun.ICON)
		self.connect('destroy', self.on_close_application)
		#
		vbox = Gtk.VBox(spacing = 5)
		vbox.set_border_width(5)
		self.get_content_area().add(vbox)
		hbox = Gtk.HBox()
		vbox.pack_start(hbox,True,True,0)
		#
		button_b1 = Gtk.Button()
		button_b1.set_size_request(40,40)
		button_b1.set_tooltip_text(_('Scan'))	
		button_b1.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_FIND,Gtk.IconSize.BUTTON))
		button_b1.connect('clicked',self.on_button_scan_clicked)		
		hbox.pack_start(button_b1,False,False,0)	
		#
		button_quit = Gtk.Button()
		button_quit.set_size_request(40,40)
		button_quit.set_tooltip_text(_('Exit'))	
		button_quit.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_QUIT,Gtk.IconSize.BUTTON))
		button_quit.connect('clicked',self.on_close_application)		
		hbox.pack_end(button_quit,False,False,0)	
		#
		button_about = Gtk.Button()
		button_about.set_size_request(40,40)
		button_about.set_tooltip_text(_('About'))	
		button_about.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ABOUT,Gtk.IconSize.BUTTON))
		button_about.connect('clicked',self.on_button_about_clicked)		
		hbox.pack_end(button_about,False,False,0)	
		#
		button_update = Gtk.Button()
		button_update.set_size_request(40,40)
		button_update.set_tooltip_text(_('Update virus database'))	
		button_update.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_REFRESH,Gtk.IconSize.BUTTON))
		button_update.connect('clicked',self.on_button_update_clicked)		
		hbox.pack_end(button_update,False,False,0)	
		#
		frame0 = Gtk.Frame()
		vbox.pack_start(frame0,True,True,0)
		vbox0 = Gtk.VBox(spacing = 5)
		vbox0.set_border_width(5)
		frame0.add(vbox0)
		#
		label1 = Gtk.Label()
		label1.set_text(_('ClamAV version')+': '+ self.scanner.version().split(' ')[1].split('/')[0])
		label1.set_alignment(0, 0.5)
		vbox0.pack_start(label1,False,False,0)
		#
		frame1 = Gtk.Frame()
		vbox.pack_start(frame1,True,True,0)
		hbox1 = Gtk.HBox(spacing = 5)
		hbox1.set_border_width(5)
		frame1.add(hbox1)
		#
		scrolledwindow = Gtk.ScrolledWindow()
		scrolledwindow.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
		scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)		
		scrolledwindow.set_size_request(700,500)
		hbox1.pack_start(scrolledwindow,True,True,0)		
		model = Gtk.ListStore(bool,bool,str)
		self.treeview = Gtk.TreeView()
		self.treeview.set_model(model)
		scrolledwindow.add(self.treeview)
		crt0 = Gtk.CellRendererToggle()
		crt0.set_property('activatable',True)
		column0 = Gtk.TreeViewColumn(_('Scan'),crt0,active=0)
		crt0.connect("toggled", self.toggled_cb, (model, 0))
		self.treeview.append_column(column0)
		crt1 = Gtk.CellRendererToggle()
		crt1.set_property('activatable',True)
		column1 = Gtk.TreeViewColumn(_('Rec.'),crt1,active=1)
		crt1.connect("toggled", self.toggled_cb, (model, 1))
		self.treeview.append_column(column1)
		#
		column = Gtk.TreeViewColumn(_('Folder'),Gtk.CellRendererText(),text=2)
		self.treeview.append_column(column)
		
		#
		vbox1 = Gtk.VBox()
		hbox1.pack_end(vbox1,False,False,0)
		button1 = Gtk.Button()
		button1.set_size_request(40,40)
		button1.set_tooltip_text(_('Add'))	
		button1.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_ADD,Gtk.IconSize.BUTTON))
		button1.connect('clicked',self.on_button1_clicked)		
		vbox1.pack_start(button1,False,False,0)
		button2 = Gtk.Button()
		button2.set_size_request(40,40)
		button2.set_tooltip_text(_('Remove'))	
		button2.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_REMOVE,Gtk.IconSize.BUTTON))
		button2.connect('clicked',self.on_button2_clicked)		
		vbox1.pack_start(button2,False,False,0)
		button3 = Gtk.Button()
		button3.set_size_request(40,40)
		button3.set_tooltip_text(_('Remove all folders'))	
		button3.set_image(Gtk.Image.new_from_stock(Gtk.STOCK_CLEAR,Gtk.IconSize.BUTTON))
		button3.connect('clicked',self.on_button3_clicked)		
		vbox1.pack_end(button3,False,False,0)
		#
		self.from_nautilus = from_nautilus
		self.load_preferences()
		#
		if len(folders)>0:
			model = self.treeview.get_model()
			model.clear()
			for folder in folders:
				model.append([True,True,folder])			
		#
		self.show_all()
		
	def on_close_application(self,widget):
		self.save_preferences()
		self.hide()
		self.destroy()
		
	def toggled_cb(self,cell, path, user_data):
		model, column = user_data
		model[path][column] = not model[path][column]
		self.save_preferences()
		return
		
	def load_preferences(self):
		configuration = Configuration()
		model = self.treeview.get_model()
		model.clear()
		if self.from_nautilus:
			folders = configuration.get('folders')
			for folder in folders:
				scan = folder['scan']
				recursive = folder['recursive']
				folder_name = folder['name']
				model.append([scan,recursive,folder_name])
	
	def save_preferences(self):
		folders = []
		configuration = Configuration()
		if self.from_nautilus:
			model = self.treeview.get_model()
			itera=model.get_iter_first()
			while(itera!=None):
				folder = {}
				folder['scan'] = model.get(itera, 0)[0]
				folder['recursive'] = model.get(itera, 1)[0]
				folder['name'] = model.get(itera, 2)[0]
				folders.append(folder)
				itera=model.iter_next(itera)
			configuration.set('folders',folders)
		configuration.save()
		
	def on_button1_clicked(self,widget):
		dialog = Gtk.FileChooserDialog(_('Select Folder...'),None,Gtk.FileChooserAction.SELECT_FOLDER,(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)) 
		dialog.set_default_response(Gtk.ResponseType.OK)
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			if not self.exists_folder(dialog.get_filename()):
				model = self.treeview.get_model()
				model.append([True,False,dialog.get_filename()])
		dialog.destroy()

	def exists_folder(self,folder):
		exists=False
		model = self.treeview.get_model()
		itera=model.get_iter_first()
		while(itera!=None):
			value=model.get(itera, 2)[0]
			itera=model.iter_next(itera)
			if value==folder:
				itera=None
				exists=True
		return exists

	def on_button2_clicked(self,widget):
		selected=self.treeview.get_selection()
		model = self.treeview.get_model()
		if selected!=None:
			if selected.get_selected()[1]!=None:
				model.remove(selected.get_selected()[1])

	def on_button3_clicked(self,widget):
		model = self.treeview.get_model()
		model.clear()
	
	def on_button_scan_clicked(self,widget):
		infectados=[]
		files=[]
		model = self.treeview.get_model()
		itera=model.get_iter_first()
		while(itera!=None):
			scan=self.convert_to_bool(model.get(itera, 0)[0])
			recursive=self.convert_to_bool(model.get(itera, 1)[0])
			folder=model.get(itera, 2)[0]
			if scan==True:
				self.get_files(files,folder,recursive)
			itera=model.iter_next(itera)
		infectados = self.scan_files(files)
		md = Gtk.MessageDialog()
		md.set_title('Antiviral')
		md.set_property('message_type',Gtk.MessageType.INFO)
		md.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
		md.set_property('text',_('Antiviral'))
		if len(infectados)>0:
			md.format_secondary_text(_('What a pity!, In this machine there are viruses!'))
			md.run()
			md.destroy()			
			actions=Actions(self,infectados)
			actions.run()
			actions.destroy()
		else:
			md.format_secondary_text(_('Congratulations!!, no viruses found'))
			md.run()
			md.destroy()
			

	def on_button_update_clicked(self,widget):
		self.update_database()

	def on_button_about_clicked(self,widget):
		ad=Gtk.AboutDialog()
		ad.set_name(comun.APPNAME)
		ad.set_version(comun.VERSION)
		ad.set_copyright('Copyrignt (c) 2010 - 2016\nLorenzo Carbonell')
		ad.set_comments(_('A graphical interface for\nClamAV'))
		ad.set_license(_('This program is free software: you can redistribute it and/or modify it\n\
		under the terms of the GNU General Public License as published by the\n\
		Free Software Foundation, either version 3 of the License, or (at your option)\n\
		any later version.\n\n\
		This program is distributed in the hope that it will be useful, but\n\
		WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY\n\
		or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for\n\
		more details.\n\n\
		You should have received a copy of the GNU General Public License along with\n\
		this program.  If not, see <http://www.gnu.org/licenses/>.'))		
		ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
		ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))		
		ad.set_website('http://www.atareao.es')
		ad.set_website_label('http://www.atareao.es')
		ad.set_authors(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_documenters(['Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
		ad.set_program_name('Antiviral')
		ad.run()
		ad.hide()
		ad.destroy()
			
	def convert_to_bool(self,value):
		if (value==True) or (value=='True'):
			return True
		return False
		
	def update_database(self):
		p = subprocess.Popen(['gksu','freshclam'], bufsize=10000, stdout=subprocess.PIPE)
		output = p.communicate()[0] # store stdout
		msg=''
		print(output)
		for line in output.decode().split('\n'):
			if line.find('main')!=-1:				
				if line.find('is up to date')!=-1:
					msg=_('main is up to date\n')
				else:
					msg=_('main updated\n')
			if line.find('daily')!=-1:
				if line.find('is up to date')!=-1:
					msg+=_('daily is up to date\n')
				else:
					msg+=_('daily updated\n')
			if line.find('bytecode')!=-1:
				if line.find('is up to date')!=-1:
					msg+=_('bytecode is up to date\n')
				else:
					msg+=_('bytecode updated\n')		
		if msg=='':
			msg=output
			tipo=Gtk.MessageType.ERROR
			md = Gtk.MessageDialog(self, 0, tipo,Gtk.ButtonsType.CLOSE, msg)
			md.set_title('Antiviral')
			md.run()
			md.destroy()
		else:
			tipo=Gtk.MessageType.INFO
			msg += '\n\n'+_('Reloading')+'...'
			md = Gtk.MessageDialog(self, 0, tipo,Gtk.ButtonsType.CLOSE, msg)
			md.set_title('Antiviral')
			md.run()
			md.destroy()		
			print(self.scanner.reload())
		
	def get_files(self,files,folder,recursive):
		try:
			for a_file in os.listdir(folder):
				a_file=os.path.join(folder,a_file)
				if os.path.isfile(a_file):
					files.append(a_file)
				elif os.path.isdir(a_file):
					if recursive==True:
						self.get_files(files,a_file,True)
		except Exception as e:
			print(e)
	
	def scan_files(self,files):
		infectados=[]
		if len(files)>0:
			p=Progreso(_('Scanning...'),self,len(files))
			for a_file in files:
				p.set_scanning_file(a_file)
				print(a_file)
				ret=self.scanner.multiscan_file(a_file)
				if ret:
					if ret[a_file][0]=='FOUND':
						infectado = {'file':a_file,'virus':ret[a_file][1]}
						infectados.append(infectado)
				p.increase()
				if p.get_stop()==True:
					p.hide()
					p.destroy()
					return infectados
			p.destroy()
		return infectados
			
def main():
	print(pyclamav.version())
	print(pyclamav.get_version())
	print(pyclamav.get_numsig())
	folder='/home/atareao/Dropbox/Movilidad/'
	for file in os.listdir(folder):
		ret=pyclamav.scanfile(folder+file)
		if ret[0]==0:
			print(file+" -> OK")
		else:
			print(file+" -> Infected!!!! "+ret[1])
	return 0

if __name__ == '__main__':
	av=Antiviral()
	av.run()
	av.destroy()
