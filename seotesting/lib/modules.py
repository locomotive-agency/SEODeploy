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
import sys
import importlib

from .config import Config
from .logging import get_logger
from .exceptions import ModuleNotImplemented


_LOG = get_logger(__name__)


class ModuleBase(object):

    def __init__(self, config=None, samples=[]):
        self.messages = []
        self.samples = samples
        self.config = config or Config()


    def prepare_messages(self, data):
        """ Data should be in format of
            [{'path': <str>, 'url': <str>, 'issue': <str>}, ...]

            Output in format:
            [{'module': <str>, 'path': <str>, 'url': <str>, 'issue': [list]}, ...]
        """
        path_data = {}
        for i in data:

            # Consolidate rows:
            if i['path'] in path_data:
                path_data[i['path']]['issues'].append(i['issue'])
            else:
                path_data[i['path']] = {'url':i.url, issues:[i['issue']]}

        mesages = [{'module': self.modulename, 'path': k, 'url': v['url'], 'issues': v['issues']} for k,v in path_data.items()]

        self.messages.extend(messages)

        return mesages


    def run(self, samples):
        raise NotImplementedError




class ModuleConfig(object):

    def __init__(self, config=None, mdirs=[]):

        self.module_names = None
        self.module_path = None
        self.config = config or Config()
        self.mdirs = mdirs + ['modules']
        self.data  = self._get_module_data()

        self.paths = self._get_module_paths(self.data)
        self.names = self._get_module_names(self.data)

        self.modules = self.ModuleObjects()

        self.build_modules()


    class ModuleObjects(object): pass


    def build_modules(self):

        sys.path.append(self.module_path)

        for k,v in self.data.items():
            if v['is_config']:
                setattr(self.modules, k, importlib.import_module(k))


    def _is_confugured(self, module):

        if hasattr(self.config, 'modules_activated'):
            return module in list(self.config.modules_activated.keys())
        return False


    def _get_module_data(self):

        for dir in self.mdirs:

            dir = os.path.join(os.path.dirname(__file__), '..', dir)

            if not os.path.isdir(dir):
                continue
            else:
                break

        else:
            raise ModuleNotImplemented('Modules directory not found in: {}'.format(','.join(self.mdirs)))

        self.module_path = dir

        return { f.name:{'name':f.name, 'path': f.path, 'mdir': dir, 'is_config': self._is_confugured(f.name)} for f in os.scandir(dir) if f.is_dir()}


    def _get_module_names(self, data):
        return [k for k,v in data.items() if v['is_config'] ]


    def _get_module_paths(self, data):
        return [v['path'] for k,v in data.items() if v['is_config'] ]
