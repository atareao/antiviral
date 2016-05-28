#! /usr/bin/python
# -*- coding: iso-8859-15 -*-
#
# <one line to give the program's name and a brief idea of what it does.>
#
# Copyright (C) 2010 Lorenzo Carbonell
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


import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
from gi.repository import GObject


class Progreso(Gtk.Dialog):
    __gsignals__ = {
        'i-want-stop': (GObject.SIGNAL_RUN_FIRST, GObject.TYPE_NONE, ()),
    }

    def __init__(self, title, parent, max_value):
        Gtk.Dialog.__init__(self, title, parent)
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_size_request(330, 30)
        self.set_resizable(False)
        self.connect('destroy', self.close)
        vbox = Gtk.VBox(spacing=5)
        vbox.set_border_width(5)
        self.get_content_area().add(vbox)
        #
        frame1 = Gtk.Frame()
        vbox.pack_start(frame1, True, True, 0)
        vbox1 = Gtk.VBox(spacing=5)
        vbox1.set_border_width(5)
        frame1.add(vbox1)
        #
        self.label = Gtk.Label()
        vbox1.pack_start(self.label, True, True, 0)
        #
        self.progressbar = Gtk.ProgressBar()
        vbox1.pack_start(self.progressbar, True, True, 0)
        #
        hbox = Gtk.HBox()
        vbox.pack_start(hbox, False, False, 0)
        button_stop = Gtk.Button()
        button_stop.set_size_request(40, 40)
        button_stop.set_image(
            Gtk.Image.new_from_stock(Gtk.STOCK_STOP, Gtk.IconSize.BUTTON))
        button_stop.connect('clicked', self.on_button_stop_clicked)
        hbox.pack_end(button_stop, False, False, 0)
        self.stop = False
        self.show_all()
        self.max_value = max_value
        self.value = 0.0

    def get_stop(self):
        return self.stop

    def on_button_stop_clicked(self, widget):
        print('button pressed')
        self.stop = True
        self.emit('i-want-stop')

    def set_scanning_file(self, afile):
        if len(afile) > 35:
            text = '...'+afile[-32:]
        else:
            text = afile
        self.label.set_label(text)

    def set_value(self, value):
        if value >= 0 and value <= self.max_value:
            self.value = value
            fraction = self.value/self.max_value
            self.progressbar.set_fraction(fraction)
            if self.value == self.max_value:
                self.hide()

    def close(self, widget=None):
        self.destroy()

    def increase(self):
        self.value += 1.0
        fraction = self.value/self.max_value
        self.progressbar.set_fraction(fraction)
        if self.value == self.max_value:
            self.hide()

    def decrease(self):
        self.value -= 1.0
        fraction = self.value/self.max_value
        self.progressbar.set_fraction(fraction)

if __name__ == '__main__':
    p = Progreso('Prueba', None, 100)
    p.run()
