#! /usr/bin/env python
# coding: utf-8
#
# Copyright (c) 2020 JR Oakes
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os

from parse_it import ParseIt



class Config(object):

    def __init__(self, module=None, dirs=[], cfiles=[]):
        self.dirs = ['.modules', 'lib/modules','seotesting/lib/modules'] + dirs
        self.cfiles = ['seotesting_config.yaml'] + cfiles
        self.vars = {}
        self.modules = []
        self.module = module

        super(Config, self).__init__()

        self.build()

    def _load_modules(self):
        for dir in self.dirs:
            try:
                self.modules.extend([module for module in os.listdir(dir) if os.path.isdir(os.path.join(dir, module))])
                break
            except FileNotFoundError:
                pass

    def _load_configs(self):
        for cfile in self.cfiles:
            try:
                parser = ParseIt(config_location=cfile, config_type_priority=['cli_args', 'yaml'])
                vars = parser.read_all_configuration_variables()

                if self.module:
                    vars = vars['modules'][self.module]

                for name,value in vars.items():
                    self.__setattr__(name, value)

            except FileNotFoundError:
                pass


    def build(self):
        self._load_modules()
        self._load_configs()


    def __setattr__(self, name, value):
        super().__setattr__(name.lower(), value)

    def __getattribute__(self, name):
        return super().__getattribute__(name.lower())
