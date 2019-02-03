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

INCH = 25.4

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

def AxiConnect():
    app = App.get_running_app()

    min_height = app.ad.options.pen_pos_down
    max_height = app.ad.options.pen_pos_up

    app.ad.connect()
    app.ad.options.units = 0
    app.ad.options.model = 2
    app.ad.options.pen_pos_down = min_height
    app.ad.options.pen_pos_up = max_height
    app.ad.update()

    # app.ad.turtle_x = app.head_pos[0]
    # app.ad.turtle_y = app.head_pos[1]

    return app.ad


def AxiDisconnect(axi):
    axi.disconnect()

    app = App.get_running_app()
    
    # app.head_pos[0] = axi.turtle_x
    # app.head_pos[1] = axi.turtle_y

    app.root.ids['status_label'].text = 'x: {:.1f}mm'.format(app.head_pos[0]*INCH) + '   y: {:.1f}mm'.format(app.head_pos[1]*INCH)


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
    def coorner(self, coorner):
        x = 0.0
        y = 0.0

        pos_x = 0.0
        pos_y = 0.0

        # current position
        app = App.get_running_app()
        # pos_x = app.head_pos[0]
        # pos_y = app.head_pos[1]

        axi = AxiConnect()

        if coorner == 0:
            x = axi.x_bounds_min - pos_x
            y = axi.y_bounds_min - pos_y
        elif coorner == 1:
            x = axi.x_bounds_max - pos_x
            y = axi.y_bounds_min - pos_y
        elif coorner == 2:
            x = axi.x_bounds_min - pos_x
            y = axi.y_bounds_max - pos_y
        elif coorner == 3:
            x = axi.x_bounds_max - pos_x
            y = axi.y_bounds_max - pos_y

        # axi.move(x, y)
        # axi.plotSegmentWithVelocity(x, y, 0, 0)

        app.head_pos[0] = x
        app.head_pos[1] = y

        AxiDisconnect(axi)

    # Move pen up/down
    def pen(self, state):
        axi = AxiConnect()

        if state == 0:
            axi.penup()
        elif state == 1:
            axi.pendown()

        AxiDisconnect(axi)

    # move pen relativelly
    def move(self, x, y):
        app = App.get_running_app()
        pos_x = app.head_pos[0]
        pos_y = app.head_pos[1]

        pos_x += x / INCH # to mm
        pos_y += y / INCH # to mm
        
        axi = AxiConnect()

        # axi.move(x, y)
        # axi.plotSegmentWithVelocity(pos_x, pos_y, 0, 0)

        app.head_pos[0] = pos_x
        app.head_pos[1] = pos_y
        
        AxiDisconnect(axi)

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

        # app.root.ids['flyover_button'].enabled = True
        app.root.ids['plot_button'].enabled = True

        self.dismiss_popup()

    def flyover(self):
        app = App.get_running_app()
        print('FLY OVER', app.filename)
    
    def plot(self):
        app = App.get_running_app()
        print('PLOT', app.filename)

        app.ad.effect( app.head_pos )
        app.head_pos[0] = app.ad.svg_last_known_pos_x
        app.head_pos[1] = app.ad.svg_last_known_pos_y
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
