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

    # SET
    def setPenDown(self, min_height):
        app = App.get_running_app()
        max_height = app.ad.options.pen_pos_up

        app.ad.connect()
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()
        app.ad.penup()
        app.ad.pendown()
        app.ad.disconnect()

    def setPenUp(self, max_height):
        app = App.get_running_app()
        min_height = app.ad.options.pen_pos_down

        app.ad.connect()
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()
        app.ad.pendown()
        app.ad.penup()
        app.ad.disconnect()

    # MOVE
    #  go to absoluite coorners
    def goCoorner(self, coorner):
        app = App.get_running_app()
        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up
        
        app.ad.connect()
        app.ad.options.units = 0
        app.ad.options.model = 2
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()

        if coorner == 0:
            app.ad.moveto(app.ad.x_bounds_min, app.ad.y_bounds_min)
        elif coorner == 1:
            app.ad.moveto(app.ad.x_bounds_max, app.ad.y_bounds_min)
        elif coorner == 2:
            app.ad.moveto(app.ad.x_bounds_min, app.ad.y_bounds_max)
        elif coorner == 3:
            app.ad.moveto(app.ad.x_bounds_max, app.ad.y_bounds_max)

        app.ad.disconnect()
        app.head_pos[0] = app.ad.f_curr_x
        app.head_pos[1] = app.ad.f_curr_y
        app.root.ids['status_label'].text = 'x:' + str(app.head_pos[0]) + '  y:' + str(app.head_pos[1])


    # Move pen up/down
    def pen(self, state):
        app = App.get_running_app()
        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up

        app.ad.connect()
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()

        if state == 0:
            app.ad.penup()
        elif state == 1:
            app.ad.pendown()

        app.ad.disconnect()

    # move pen relativelly
    def go(self, x, y):
        app = App.get_running_app()
        min_height = app.ad.options.pen_pos_down
        max_height = app.ad.options.pen_pos_up

        app.ad.connect()
        app.ad.options.units = 0
        app.ad.options.model = 2
        app.ad.options.pen_pos_down = min_height
        app.ad.options.pen_pos_up = max_height
        app.ad.update()

        app.ad.move(x, y)

        app.ad.disconnect()
        app.head_pos[0] = app.ad.f_curr_x
        app.head_pos[1] = app.ad.f_curr_y
        app.root.ids['status_label'].text = 'x:' + str(app.head_pos[0]) + ',' + str(app.head_pos[1])

    # FILE
    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load a SVG file to print", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        

    def load(self, filenames):
        app = App.get_running_app()
        app.filename = filenames[0]
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

        app.root.ids['flyover_button'].enabled = True
        app.root.ids['plot_button'].enabled = True

        self.dismiss_popup()

    def flyover(self):
        app = App.get_running_app()
        print('FLY OVER', app.filename)
    
    def plot(self):
        app = App.get_running_app()
        print('PLOT', app.filename)

        app.ad.effect( app.head_pos )
        app.head_pos[0] = app.ad.f_curr_x
        app.head_pos[1] = app.ad.f_curr_y
        app.root.ids['status_label'].text = 'x:' + str(app.head_pos[0]) + ',' + str(app.head_pos[1])

class AxiPrinter(App):
    ad = axidraw.AxiDraw() 
    filename = "None"
    head_pos = [0.0, 0.0]

    def build(self):
        self.ad.interactive()
        self.head_pos = [0.0, 0.0]
        self.ad.turtle_x = 0.0
        self.ad.turtle_y = 0.0
        self.ad.f_curr_x = 0.0
        self.ad.f_curr_y = 0.0
        return Builder.load_file('AxiPrinter.kv') 


if __name__ == '__main__':
    AxiPrinter().run()
