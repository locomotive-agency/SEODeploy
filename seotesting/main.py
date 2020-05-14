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

import lib.contentking as ck
import lib.sampling as sampling
import lib.modules as modules
import lib.exceptions as exceptions

from lib.logging import get_logger
from lib.config import Config

_LOG = get_logger(__name__)


class SEOTesting(object):

    def __init__(self, config):

        self.config = config or Config()
        self.messages = []
        self.samples = None
        self.modules = None
        self.summary = None



    def execute(self):

        self.summary = {'started': datetime.now()}

        # Get Sample Paths
        self.samples = sampling.get_samples(self.config)
        self.summary.update({'samples': len(self.samples)})

        # get Modules
        self.modules = modules.get_module_names(self.config)
        self.summary.update({'modules': self.modules})






    def create_message(self, data):
        self.messages.append(data)


    def get_messages(self):
        return pd.DataFrame(self.messages)




if __name__ == '__main__':
    cli()
