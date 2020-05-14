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

from datetime import datetime
import pandas as pd
import json

from .lib.modules import ModuleConfig
from .lib.sampling import get_sample_paths
from .lib.logging import get_logger
from .lib.config import Config

_LOG = get_logger(__name__)


class SEOTesting(object):

    def __init__(self, config=None):

        self.config = config or Config()
        self.messages = []
        self.module_config = ModuleConfig(self.config)

        self.samples = None
        self.modules = None
        self.summary = None



    def execute(self):

        self.summary = {'started': datetime.now()}

        # Get Sample Paths
        self.samples = get_sample_paths(self.config)
        self.summary.update({'samples': len(self.samples)})

        # get Modules
        self.modules = self.module_config.module_names
        self.summary.update({'modules': ','.join(self.modules)})

        for module in self.module_config.active_modules:

            module = self.module_config.active_modules[module].SEOTestingModule()

            passing, messages = module.run(self.samples)

            self.update_messages(messages)

            self.summary.update({'{} passing: '.format(module.modulename): passing})



        df = self.get_messages().to_csv('output.csv', index=False)

        print('Run CSV saved to:', 'output.csv')
        print()
        print('Run Summary')
        print(json.dumps(self.summary, indent=2))







    def update_messages(self, messages):
        self.messages.extend(data)


    def get_messages(self):
        return pd.DataFrame(self.messages)




if __name__ == '__main__':
    cli()
