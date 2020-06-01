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

from seodeploy.lib.modules import ModuleBase
from seodeploy.lib.config import Config
from .functions import run_path_pings, run_check_results, load_report


class SEOTestingModule(ModuleBase):
    def __init__(self, config=None, samples=None):

        super(SEOTestingModule, self).__init__(config, samples)
        self.modulename = "contentking"
        self.config = config or Config(module=self.modulename)
        self.exclusions = config.contentking.ignore

        self.time_zone = pytz.timezone(self.config.contentking.TIMEZONE)


    def run(self, sample_paths):

        start_time = datetime.now().astimezone(self.time_zone)

        # Runs the sample paths against COntentKing API to ask for recrawling.
        run_path_pings(sample_paths, self.config)

        # Checks results via multi-threading
        page_data = run_check_results(
            sample_paths, start_time, self.time_zone, self.config
        )

        diffs = self.run_diffs(page_data)

        self.messages = self.prepare_messages(diffs)

        self.passing = len(messages) == 0

        return self.errors

    def get_samples(self, site_id, limit):

        report = "pages"
        pages = load_report(
            report, self.config, id=site_id, per_page=self.config.contentking.PER_PAGE
        )

        all_urls = []
        for page in pages:

            if page:
                urls = [url["url"] for url in page if url["is_indexable"]]
                all_urls.extend(urls)
            else:
                break

            if limit and len(all_urls) >= limit:
                all_urls = all_urls[:limit]
                break

        return all_urls
