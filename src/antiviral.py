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
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import GLib
import os
import pyclamd
import subprocess
import comun
from threading import Thread
from configurator import Configuration
from actions import Actions
from progreso import Progreso
from idleobject import IdleObject
from comun import _


def convert_to_bool(value):
    if (value is True) or (value == 'True'):
        return True
    return False


def get_files(folder, recursive):
    tfiles = []
    try:
        for a_file in os.listdir(folder):
            a_file = os.path.join(folder, a_file)
            if os.path.isfile(a_file) and a_file not in tfiles:
                tfiles.append(a_file)
            elif os.path.isdir(a_file):
                # print(a_file)
                if recursive is True:
                    tfiles.extend(get_files(a_file, True))
    except Exception as e:
        print(e)
    return tfiles


class ButtonWithTextAndIcon(Gtk.Button):

    def __init__(self, text=None, icon=None, size=Gtk.IconSize):
        Gtk.Button.__init__(self)
        self.set_size_request(40, 40)
        box = Gtk.HBox(False, 0)
        self.add(box)
        self.text = Gtk.Label()
        if text is not None:
            if type(text) == str:
                self.text.set_text(text)
        self.icon = Gtk.Image()
        if icon is not None:
            if type(icon) == str:
                if os.path.exists(icon):
                    self.icon = Gtk.Image.new_from_file(icon)
            elif type(icon) == Gtk.Image:
                self.icon = icon
            elif type(icon) == GdkPixbuf.Pixbuf:
                self.icon = Gtk.Imagen.new_from_pixbuf(icon)
        box.pack_start(self.icon, False, False, 5)
        box.pack_start(self.text, False, False, 5)
        self.icon.show()
        self.text.show()


class Container():

    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data

    def set_data(self, data):
        self.data = data


class FolderProcessor(Thread, IdleObject):
    __gsignals__ = {
        'to-process': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'processed': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object,)),
        }

    def __init__(self, model=None, ishome=False):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.model = model
        self.ishome = ishome
        self.daemon = True
        self.stop = False

    def stop_it(self, executor):
        self.stop = True

    def run(self):
        files = []
        if self.ishome:
            folder = os.path.expanduser("~")
            print(folder)
            self.emit('to-process', folder)
            files.extend(get_files(os.path.expanduser("~"), False))
            self.emit('processed')
        else:
            itera = self.model.get_iter_first()
            while(itera is not None):
                scan = convert_to_bool(self.model.get(itera, 0)[0])
                recursive = convert_to_bool(self.model.get(itera, 1)[0])
                folder = self.model.get(itera, 2)[0]
                print(folder)
                self.emit('to-process', folder)
                if scan is True:
                    files.extend(get_files(folder, recursive))
                itera = self.model.iter_next(itera)
                self.emit('processed')
        self.emit('finished', Container(files))


class Scanner(Thread, IdleObject):
    __gsignals__ = {
        'to-scan': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (str,)),
        'scanned': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        'infected': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, (object,)),
        'finished': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
        }

    def __init__(self, scanner, files):
        IdleObject.__init__(self)
        Thread.__init__(self)
        self.files = files
        self.scanner = scanner
        self.daemon = True
        self.stop = False

    def stop_it(self, executor):
        self.stop = True

    def run(self):
        print(2)
        if len(self.files) > 0:
            self.stop = False
            for a_file in self.files:
                self.emit('to-scan', a_file)
                print(a_file)
                ret = self.scanner.multiscan_file(a_file)
                if ret:
                    if ret[a_file][0] == 'FOUND':
                        infectado = {'file': a_file, 'virus': ret[a_file][1]}
                        self.emit('infected', infectado)
                self.emit('scanned')
                if self.stop is True:
                    break
        self.emit('finished')


class Antiviral(Gtk.Window):

    def __init__(self, from_filebrowser=False, folders=[]):
        Gtk.Window.__init__(self)
        self.set_title(_('Antiviral'))
        self.set_modal(True)
        #
        try:
            self.scanner = pyclamd.ClamdUnixSocket()
            self.scanner.ping()
        except pyclamd.ConnectionError:
            self.scanner = pyclamd.ClamdNetworkSocket()
            try:
                self.scanner.ping()
            except pyclamd.ConnectionError as e:
                print(e)
                exit(0)
        # print(self.scanner.reload())
        print(self.scanner.stats())
        #
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_title(comun.APP)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.on_close_application)
        #
        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.add(vbox)
        #
        frame0 = Gtk.Frame()
        vbox.pack_start(frame0, True, True, 0)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        frame0.add(vbox0)
        #
        label1 = Gtk.Label()
        label1.set_text(_('ClamAV version')+': ' +
                        self.scanner.version().split(' ')[1].split('/')[0])
        label1.set_alignment(0, 0.5)
        vbox0.pack_start(label1, False, False, 0)
        #
        frame1 = Gtk.Frame()
        vbox.pack_start(frame1, True, True, 0)
        hbox1 = Gtk.HBox(spacing=5)
        hbox1.set_border_width(5)
        frame1.add(hbox1)
        #
        vbox0 = Gtk.VBox()
        hbox1.pack_start(vbox0, False, False, 0)

        button_b0 = ButtonWithTextAndIcon(
            _('Scan home'), Gtk.Image.new_from_stock(
                Gtk.STOCK_FIND, Gtk.IconSize.BUTTON))
        button_b0.set_tooltip_text(_('Scan home now'))
        button_b0.connect('clicked', self.on_button_scan_home_clicked)
        vbox0.pack_start(button_b0, False, False, 0)

        button_b1 = ButtonWithTextAndIcon(
            _('Scan folders'), Gtk.Image.new_from_stock(
                Gtk.STOCK_FIND, Gtk.IconSize.BUTTON))
        button_b1.set_tooltip_text(_('Scan selected folders now'))
        button_b1.connect('clicked', self.on_button_scan_clicked)
        vbox0.pack_start(button_b1, False, False, 0)

        button_quit = ButtonWithTextAndIcon(
            _('Exit'), Gtk.Image.new_from_stock(
                Gtk.STOCK_QUIT, Gtk.IconSize.BUTTON))
        button_quit.set_tooltip_text(_('Exit'))
        button_quit.connect('clicked', self.on_close_application)
        vbox0.pack_end(button_quit, False, False, 0)
        #
        button_about = ButtonWithTextAndIcon(
            _('About'), Gtk.Image.new_from_stock(
                Gtk.STOCK_ABOUT, Gtk.IconSize.BUTTON))
        button_quit.set_tooltip_text(_('About'))
        button_about.connect('clicked', self.on_button_about_clicked)
        vbox0.pack_end(button_about, False, False, 0)
        #
        button_update = ButtonWithTextAndIcon(
            _('Update'), Gtk.Image.new_from_stock(
                Gtk.STOCK_REFRESH, Gtk.IconSize.BUTTON))
        button_update.set_tooltip_text(_('Update virus database'))
        button_update.connect('clicked', self.on_button_update_clicked)
        vbox0.pack_end(button_update, False, False, 0)

        scrolledwindow = Gtk.ScrolledWindow()
        scrolledwindow.set_policy(
            Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolledwindow.set_shadow_type(Gtk.ShadowType.ETCHED_OUT)
        scrolledwindow.set_size_request(500, 300)
        hbox1.pack_start(scrolledwindow, True, True, 0)
        model = Gtk.ListStore(bool, bool, str)
        self.treeview = Gtk.TreeView()
        self.treeview.set_model(model)
        scrolledwindow.add(self.treeview)
        crt0 = Gtk.CellRendererToggle()
        crt0.set_property('activatable', True)
        column0 = Gtk.TreeViewColumn(_('Scan'), crt0, active=0)
        crt0.connect("toggled", self.toggled_cb, (model, 0))
        self.treeview.append_column(column0)
        crt1 = Gtk.CellRendererToggle()
        crt1.set_property('activatable', True)
        column1 = Gtk.TreeViewColumn(_('Rec.'), crt1, active=1)
        crt1.connect("toggled", self.toggled_cb, (model, 1))
        self.treeview.append_column(column1)
        #
        column = Gtk.TreeViewColumn(
            _('Folder'), Gtk.CellRendererText(), text=2)
        self.treeview.append_column(column)

        #
        vbox1 = Gtk.VBox()
        hbox1.pack_end(vbox1, False, False, 0)
        button1 = Gtk.Button()
        button1.set_size_request(40, 40)
        button1.set_tooltip_text(_('Add new folder'))
        button1.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_ADD, Gtk.IconSize.BUTTON))
        button1.connect('clicked', self.on_button1_clicked)
        vbox1.pack_start(button1, False, False, 0)
        button2 = Gtk.Button()
        button2.set_size_request(40, 40)
        button2.set_tooltip_text(_('Remove selected folder'))
        button2.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_REMOVE, Gtk.IconSize.BUTTON))
        button2.connect('clicked', self.on_button2_clicked)
        vbox1.pack_start(button2, False, False, 0)
        button3 = Gtk.Button()
        button3.set_size_request(40, 40)
        button3.set_tooltip_text(_('Remove all folders'))
        button3.set_image(Gtk.Image.new_from_stock(
            Gtk.STOCK_CLEAR, Gtk.IconSize.BUTTON))
        button3.connect('clicked', self.on_button3_clicked)
        vbox1.pack_end(button3, False, False, 0)
        #
        self.from_filebrowser = from_filebrowser
        if not self.from_filebrowser:
            self.load_preferences()
        #
        self.progreso_dialog = None
        self.files = []
        #
        if len(folders) > 0:
            model = self.treeview.get_model()
            model.clear()
            for folder in folders:
                model.append([True, True, folder])
        #
        self.show_all()

    def on_close_application(self, widget):
        self.save_preferences()
        self.hide()
        self.destroy()

    def toggled_cb(self, cell, path, user_data):
        model, column = user_data
        model[path][column] = not model[path][column]
        self.save_preferences()
        return

    def load_preferences(self):
        configuration = Configuration()
        model = self.treeview.get_model()
        model.clear()
        folders = configuration.get('folders')
        for folder in folders:
            scan = folder['scan']
            recursive = folder['recursive']
            folder_name = folder['name']
            model.append([scan, recursive, folder_name])

    def save_preferences(self):
        if not self.from_filebrowser:
            folders = []
            model = self.treeview.get_model()
            itera = model.get_iter_first()
            while(itera is not None):
                folder = {}
                folder['scan'] = model.get(itera, 0)[0]
                folder['recursive'] = model.get(itera, 1)[0]
                folder['name'] = model.get(itera, 2)[0]
                folders.append(folder)
                itera = model.iter_next(itera)
            if len(folders) > 0:
                configuration = Configuration()
                configuration.set('folders', folders)
                configuration.save()

    def on_button1_clicked(self, widget):
        dialog = Gtk.FileChooserDialog(_(
            'Select Folder...'),
            None,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
        dialog.set_default_response(Gtk.ResponseType.OK)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            if not self.exists_folder(dialog.get_filename()):
                model = self.treeview.get_model()
                model.append([True, False, dialog.get_filename()])
        dialog.destroy()

    def exists_folder(self, folder):
        exists = False
        model = self.treeview.get_model()
        itera = model.get_iter_first()
        while(itera is not None):
            value = model.get(itera, 2)[0]
            itera = model.iter_next(itera)
            if value == folder:
                itera = None
                exists = True
        return exists

    def on_button2_clicked(self, widget):
        selected = self.treeview.get_selection()
        model = self.treeview.get_model()
        if selected is not None:
            if selected.get_selected()[1] is not None:
                model.remove(selected.get_selected()[1])

    def on_button3_clicked(self, widget):
        model = self.treeview.get_model()
        model.clear()

    def on_button_scan_home_clicked(self, widget):
        fp = FolderProcessor(ishome=True)
        self.progreso_dialog = Progreso(
            _('Processing folders...'), self, 1)
        self.progreso_dialog.connect(
            'i-want-stop', fp.stop_it)
        fp.connect('to-process', self.on_to_process_folder)
        fp.connect('processed', self.on_processed_folder)
        fp.connect('finished', self.on_processed_folders)
        fp.start()
        self.progreso_dialog.run()

    def on_button_scan_clicked(self, widget):
        model = self.treeview.get_model()
        fp = FolderProcessor(model)
        if self.progreso_dialog is not None:
            self.progreso_dialog.destroy()
            self.progreso_dialog = None
        self.progreso_dialog = Progreso(
            _('Processing folders...'), self, len(model))
        self.progreso_dialog.connect(
            'i-want-stop', fp.stop_it)
        fp.connect('to-process', self.on_to_process_folder)
        fp.connect('processed', self.on_processed_folder)
        fp.connect('finished', self.on_processed_folders)
        fp.start()
        self.progreso_dialog.run()

    def on_to_process_folder(self, processor, afile):
        # GLib.idle_add(self.progreso_dialog.set_scanning_file, afile)
        self.progreso_dialog.set_scanning_file(afile)

    def on_processed_folder(self, processor):
        # GLib.idle_add(self.progreso_dialog.increase)
        self.progreso_dialog.increase()

    def on_processed_folders(self, processor, container):
        files = container.get_data()
        if len(files) > 0:
            scanner = Scanner(self.scanner, files)
            scanner.connect('to-scan', self.going_to_scan)
            scanner.connect('scanned', self.on_progress)
            scanner.connect('infected', self.on_infected_detect)
            scanner.connect('finished', self.on_scan_finished)
            print(2)
            if self.progreso_dialog is not None:
                self.progreso_dialog.destroy()
                self.progreso_dialog = None
            print(3)
            self.progreso_dialog = Progreso(_('Scanning...'), self, len(files))
            print(4)
            self.progreso_dialog.connect(
                'i-want-stop', scanner.stop_it)
            print(5)
            self.infected = []
            print(6)
            scanner.start()
            self.progreso_dialog.run()

    def going_to_scan(self, scanner, afile):
        # GLib.idle_add(self.progreso_dialog.set_scanning_file, afile)
        self.progreso_dialog.set_scanning_file(afile)

    def on_progress(self, scanner):
        # GLib.idle_add(self.progreso_dialog.increase)
        self.progreso_dialog.increase()

    def on_infected_detect(self, scanner, infected):
        self.infected.append(infected)

    def on_scan_finished(self, scanner):
        # GLib.idle_add(self._on_scan_finished)
        if self.progreso_dialog is not None:
            self.progreso_dialog.destroy()
            self.progreso_dialog = None
        md = Gtk.MessageDialog(parent=self)
        md.set_title('Antiviral')
        md.set_property('message_type', Gtk.MessageType.INFO)
        md.add_button(Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT)
        md.set_property('text', _('Antiviral'))
        if len(self.infected) > 0:
            md.format_secondary_text(
                _('What a pity!, In this machine there are viruses!'))
            md.run()
            md.destroy()
            actions = Actions(self, self.infected)
            actions.run()
            actions.destroy()
        else:
            md.format_secondary_text(_('Congratulations!!, no viruses found'))
            md.run()
            md.destroy()

    def on_button_update_clicked(self, widget):
        self.update_database()

    def on_button_about_clicked(self, widget):
        ad = Gtk.AboutDialog()
        ad.set_name(comun.APPNAME)
        ad.set_version(comun.VERSION)
        ad.set_copyright('''
Copyrignt (c) 2010 - 2016
Lorenzo Carbonell Cerezo
''')
        ad.set_comments(_('A graphical interface for\nClamAV'))
        ad.set_license('''
This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
''')
        ad.set_logo(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_icon(GdkPixbuf.Pixbuf.new_from_file(comun.ICON))
        ad.set_website('http://www.atareao.es')
        ad.set_website_label('http://www.atareao.es')
        ad.set_authors([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_documenters([
            'Lorenzo Carbonell <lorenzo.carbonell.cerezo@gmail.com>'])
        ad.set_program_name(_('Antiviral'))
        ad.run()
        ad.hide()
        ad.destroy()

    def update_database(self):
        p = subprocess.Popen([
            'gksu', 'freshclam'], bufsize=10000, stdout=subprocess.PIPE)
        output = p.communicate()[0]  # store stdout
        msg = ''
        print(output)
        for line in output.decode().split('\n'):
            if line.find('main') != -1:
                if line.find('is up to date') != -1:
                    msg = _('main is up to date\n')
                else:
                    msg = _('main updated\n')
            if line.find('daily') != -1:
                if line.find('is up to date') != -1:
                    msg += _('daily is up to date\n')
                else:
                    msg += _('daily updated\n')
            if line.find('bytecode') != -1:
                if line.find('is up to date') != -1:
                    msg += _('bytecode is up to date\n')
                else:
                    msg += _('bytecode updated\n')
        if msg == '':
            msg = output
            tipo = Gtk.MessageType.ERROR
            md = Gtk.MessageDialog(self, 0, tipo, Gtk.ButtonsType.CLOSE, msg)
            md.set_title('Antiviral')
            md.run()
            md.destroy()
        else:
            tipo = Gtk.MessageType.INFO
            msg += '\n\n'+_('Reloading')+'...'
            md = Gtk.MessageDialog(self, 0, tipo, Gtk.ButtonsType.CLOSE, msg)
            md.set_title('Antiviral')
            md.run()
            md.destroy()
            print(self.scanner.reload())


def main():
    print(pyclamav.version())
    print(pyclamav.get_version())
    print(pyclamav.get_numsig())
    folder = '/home/atareao/Dropbox/Movilidad/'
    for file in os.listdir(folder):
        ret = pyclamav.scanfile(folder + file)
        if ret[0] == 0:
            print(file + " -> OK")
        else:
            print(file + " -> Infected!!!! "+ret[1])
    return 00

if __name__ == '__main__':
    GObject.threads_init()
    Antiviral()
    Gtk.main()
