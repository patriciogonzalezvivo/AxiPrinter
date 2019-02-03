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

from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty

from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.uix.button import Button

from pyaxidraw import axidraw

class MySlider(Slider):
    def __init__(self, **kwargs):
        self.register_event_type('on_release')
        super(MySlider, self).__init__(**kwargs)

    def on_release(self):
        pass

    def on_touch_up(self, touch):
        super(MySlider, self).on_touch_up(touch)
        if touch.grab_current == self:
            self.dispatch('on_release')
            return True

class MyButton(Button):
    enabled = BooleanProperty(True)

    def on_enabled(self, instance, value):
        if value:
            self.background_color = [1,1,1,1]
            self.color = [1,1,1,1]
        else:
            self.background_color = [1,1,1,.3]
            self.color = [1,1,1,.5]

    def on_touch_down( self, touch ):
        if self.enabled:
            return super(self.__class__, self).on_touch_down(touch)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Root(FloatLayout):
    def dismiss_popup(self):
        self._popup.dismiss()

    # MOVE
    #  go to absoluite coorners
    def goCoorner(self, coorner):
        app = App.get_running_app()
        app.ad.options.units = 0
        app.ad.update()

        if coorner == 0:
            app.ad.goto(app.ad.x_bounds_min, app.ad.y_bounds_min)
        elif coorner == 1:
            app.ad.goto(app.ad.x_bounds_max, app.ad.y_bounds_min)
        elif coorner == 2:
            app.ad.goto(app.ad.x_bounds_min, app.ad.y_bounds_max)
        elif coorner == 3:
            app.d.goto(app.ad.x_bounds_max, app.ad.y_bounds_max)

    # Move pen up/down
    def pen(self, coorner):
        app = App.get_running_app()

        # min_height = app.ad.options.pen_pos_down
        # max_height = app.ad.options.pen_pos_up
        # app.ad.options.pen_pos_down = min_height
        # app.ad.options.pen_pos_up = max_height
        app.ad.update()

        if coorner == 0:
            app.ad.penup()
        elif coorner == 1:
            app.ad.pendown()

    # move pen relativelly
    def go(self, x, y):
        app = App.get_running_app()
        app.ad.options.model = 2
        app.ad.options.units = 0
        app.ad.update()
        app.ad.move(x, y)

    # FILE
    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a SVG file to print", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        

    def load(self, filenames):
        app = App.get_running_app()
        print('Loading', app.filename)

        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up

        app.ad.plot_setup(app.filename)
        app.ad.options.model = 2
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height

        # app.ad.plot_run()

        # app.ad.options.preview = True
        # writeFile = open('current.svg','w')         # Open output file for writing.
        # writeFile.write( app.ad.plot_run( output=True ) )
        # writeFile.close()

        print(app.root.ids)
        app.root.ids['flyover_button'].enabled = True
        app.root.ids['plot_button'].enabled = True

        self.dismiss_popup()

    def flyover(self):
        app = App.get_running_app()
        print('FLY OVER', app.filename)
    
    def plot(self):
        app = App.get_running_app()
        print('PLOT', app.filename)
        app.ad.plot_run()

class AxiPrinter(App):
    ad = axidraw.AxiDraw() 
    filename = "None"

    def build(self):
        self.ad.interactive()
        return Builder.load_file('AxiPrinter.kv') 


if __name__ == '__main__':
    AxiPrinter().run()
