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


from lib.modules import ModuleBase
from lib.config import Config
from .functions import sample_function  # noqa


class SEOTestingModule(ModuleBase):

    def __init__(self, config=None, samples=None):

        super(SEOTestingModule, self).__init__(config, samples)

        self.modulename = "headless"
        self.config = config or Config(module=self.modulename)



    def run(self, samples):

        # start_time = datetime.now()

        print(len(samples))

        messages = [{'path': '/', 'url': 'https://stage.domain.com/', 'issue': 'Single headless test result'}]
        messages = self.prepare_messages(messages)

        passing = True

        return passing, messages
