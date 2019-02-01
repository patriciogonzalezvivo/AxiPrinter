#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os

import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider

from pyaxidraw import axidraw

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


class Root(FloatLayout):
    def dismiss_popup(self):
        self._popup.dismiss()


    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a SVG file to print", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        

    def load(self, filename):
        print('Loading', filename[0])

        app = App.get_running_app()

        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up

        app.ad.plot_setup(filename[0])
        app.ad.options.model = 2
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.plot_run()

        # app.ad.options.preview = True
        # writeFile = open('current.svg','w')         # Open output file for writing.
        # writeFile.write( app.ad.plot_run( output=True ) )
        # writeFile.close()

        self.dismiss_popup()

    def goCoorner(self, coorner):
        app = App.get_running_app()

        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up

        app.ad.options.model = 2
        app.ad.options.units = 0
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()
        app.ad.penup()

        if coorner == 0:
            ad.goto(app.ad.x_bounds_min, app.ad.y_bounds_min)
        elif coorner == 1:
            ad.goto(app.ad.x_bounds_max, app.ad.y_bounds_min)
        elif coorner == 2:
            ad.goto(app.ad.x_bounds_min, app.ad.y_bounds_max)
        elif coorner == 3:
            ad.goto(app.ad.x_bounds_max, app.ad.y_bounds_max)

        app.ad.pendown()



class AxiPrinter(App):
    ad = axidraw.AxiDraw() 

    def build(self):
        self.ad.interactive()
        return Builder.load_file('AxiPrinter.kv') 


if __name__ == '__main__':
    AxiPrinter().run()
