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

import pytz

from seotesting.lib.modules import ModuleBase
from seotesting.lib.config import Config
from .functions import run_path_pings, run_check_results


class ContentKingModule(ModuleBase):

    def __init__(self, config=None, samples=[]):

        super(ContentKingModule, self).__init__(config, samples)
        self.config = config or Config(module='contentking')
        self.time_zone = pytz.timezone(self.config.TIMEZONE)


    def run(self, samples):

        start_time = datetime.now().astimezone(self.time_zone).isoformat(timespec='seconds')

        # Runs the sample paths against COntentKing API to ask for recrawling.
        path_pings = run_path_pings(samples, self.config)

        # Checks results via multi-threading
        passing, results = run_check_results(samples, start_time, self.time_zone, self.config)

        messages = self.prepare_messages(data)

        return passing, messages
