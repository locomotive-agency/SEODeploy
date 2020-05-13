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
import importlib

from .config import Config
from .logging import get_logger


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




class Modules(object):

    def __init__(self, config=None):

        self.module_names = None
        self.config = config or Config()
        self.data  = self._get_module_data(config)

        self.paths = self._get_module_paths(self.data)
        self.names = self._get_module_names(self.data)


    def build_modules():

        for path in self.paths:
            importlib.import_module(path)


    def _is_confugured(module):

        if 'modules' in self.config:
            return module in list(config['modules'].keys())
        return False


    def _get_module_data(config):


        if 'module_directory' in config:
            dir = config['module_directory']
        else:
            dir = 'modules'

        if not os.path.isdir(dir):
            dir = os.path.join(os.path.dirname(__file__), '..', dir)


        return { f.name:{'name':f.name, 'path': f.path, 'is_config': _is_configured(f.name)} for f in os.scandir(dir) if f.is_dir()}


    def _get_module_names(data):
        return [k['name'] for k,v in data.items() if v['is_config'] ]


    def _get_module_paths(data):
        return [v['path'] for k,v in data.items() if v['is_config'] ]
