# -*- coding: utf-8 -*-
#Copyright (c) 2014 Walter Bender

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# You should have received a copy of the GNU General Public License
# along with this library; if not, write to the Free Software
# Foundation, 51 Franklin Street, Suite 500 Boston, MA 02110-1335 USA

import os
import subprocess
from gi.repository import Vte
from gettext import gettext as _

from gi.repository import Gtk
from gi.repository import GLib

from sugar3.activity import activity
from sugar3.activity.widgets import StopButton
from sugar3.activity.widgets import ActivityToolbarButton
from sugar3.graphics.toolbarbox import ToolbarBox
from sugar3.graphics import style

from graphics import Graphics

import logging
_logger = logging.getLogger('makey-makey')


class MakeyMakey(activity.Activity):
    ''' Enable Makey Makey device: See http://dev.laptop.org/ticket/12616 '''

    def __init__(self, handle):
        try:
            super(MakeyMakey, self).__init__(handle)
        except dbus.exceptions.DBusException, e:
            _logger.error(str(e))

        self._setup_toolbars()
        self.modify_bg(Gtk.StateType.NORMAL,
                       style.COLOR_WHITE.get_gdk_color())

        self.bundle_path = activity.get_bundle_path()
        center_in_panel = Gtk.Alignment.new(0.5, 0, 0, 0)
        url = os.path.join(self.bundle_path, 'makeymakey.html')
        graphics = Graphics()
        graphics.add_uri('file://' + url)
        graphics.set_zoom_level(0.667)
        center_in_panel.add(graphics)
        graphics.show()
        self.set_canvas(center_in_panel)
        center_in_panel.show()

        self._vt_command()

    def _vt_command(self, command='stop'):
        vt = Vte.Terminal()
        success_, pid = vt.fork_command_full(
            Vte.PtyFlags.DEFAULT,
            os.environ["HOME"],
            # ["/bin/bash"], 
            ['/usr/bin/sudo', '/usr/bin/systemctl', command, 'olpc-kbdshim'],
            [],
            GLib.SpawnFlags.DO_NOT_REAP_CHILD,
            None,
            None)
        _logger.error('VTE %s %s' % (str(success_), str(pid)))

    def can_close(self):
        _logger.error('can close')
        self._vt_command(command='start')
        return True

    def _setup_toolbars(self):
        ''' Setup the toolbars. '''
        self.max_participants = 1  # No sharing

        toolbox = ToolbarBox()

        self.activity_button = ActivityToolbarButton(self)
        toolbox.toolbar.insert(self.activity_button, 0)
        self.activity_button.show()

        self.set_toolbar_box(toolbox)
        toolbox.show()
        self.toolbar = toolbox.toolbar

        separator = Gtk.SeparatorToolItem()
        separator.props.draw = False
        separator.set_expand(True)
        toolbox.toolbar.insert(separator, -1)
        separator.show()

        stop_button = StopButton(self)
        stop_button.props.accelerator = '<Ctrl>q'
        toolbox.toolbar.insert(stop_button, -1)
        stop_button.show()
