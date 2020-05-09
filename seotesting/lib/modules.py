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

from lib.config import Config

_LOG = get_logger(__name__)


class ModuleBase(object):

    def __init__(self, config= None, samples=[]):
        self.messages = []
        self.samples = samples
        self.config = config or Config()


    def run(self, samples):
        raise NotImplementedError


def _is_confugured(module)
    config = Config()
    if 'modules' in config:
        return module in list(config['modules'].keys())
    return False


def get_module_data(config = None):

    config = config or Config()

    if 'module_directory' in config:
        dir = config['module_directory']
    else:
        dir = 'modules'

    if not os.path.isdir(dir):
        dir = os.path.join(os.path.dirname(__file__), '..', dir)

    return { f.name:{'name':f.name, 'path': f.path, 'is_config': _is_configured(f.name)} for f in os.scandir(dir) if f.is_dir()}


def get_module_names(config=None):
    return [k['name'] for k,v in get_module_data(config).items() if v['is_config'] ]


def get_module_paths(dir='modules'):
    return [v['path'] for k,v in get_module_data(config).items() if v['is_config'] ]
