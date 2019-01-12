#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider

from pyaxidraw import axidraw

# up_pos = 75
# down_pos = 25

# KV = '''


# '''

class ModifiedSlider(Slider):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(ModifiedSlider, self).__init__(**kwargs)

    def on_release(self):
        pass

    def on_touch_up(self, touch):
        super(ModifiedSlider, self).on_touch_up(touch)
        if touch.grab_current == self:
            self.dispatch('on_release')
            return True


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)

# ad = axidraw.AxiDraw() # Initialize class

class Root(FloatLayout):
    def dismiss_popup(self):
        self._popup.dismiss()


    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a SVG file to print", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()


    def go_home(self):
        app = App.get_running_app()
        app.ad.penup()
        app.ad.goto(0,0)


    def load(self, filename):
        print('Loading', filename[0])

        app = App.get_running_app()
        app.ad.plot_setup(filename[0])
        app.ad.options.model = 2
        self.dismiss_popup()

        # app.ad.plot_run( output=True )

        app.ad.options.preview = True
        writeFile = open('text.svg','w')         # Open output file for writing.
        writeFile.write( app.ad.plot_run( output=True ) )
        writeFile.close()

        


class AxiPrinter(App):
    ad = axidraw.AxiDraw() 
    # pass

    def build(self):
        self.ad.interactive()



if __name__ == '__main__':
    AxiPrinter().run()