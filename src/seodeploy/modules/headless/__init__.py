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

"""Headless Module for SEODeploy."""

import os

from seodeploy.lib.modules import ModuleBase
from seodeploy.lib.config import Config

CONFIG = Config(module="headless")

os.environ["PYPPETEER_CHROMIUM_REVISION"] = str(
    CONFIG.headless.PYPPETEER_CHROMIUM_REVISION
)

from seodeploy.modules.headless.functions import run_render  # noqa


class SEOTestingModule(ModuleBase):

    """SEODeploy Module: Headless Module."""

    def __init__(self, config=None, sample_paths=None):
        """"Initialize SEOTestingModule Class."""

        super(SEOTestingModule, self).__init__(config, sample_paths)
        self.modulename = "headless"
        self.config = config or Config(module=self.modulename)
        self.exclusions = self.config.headless.ignore

    def run(self, sample_paths=None):
        """Run the Headless Module."""

        self.sample_paths = sample_paths or self.sample_paths

        page_data = run_render(self.sample_paths, self.config)

        diffs, errors = self.run_diffs(page_data)

        self.messages = self.prepare_messages(diffs)

        return self.messages, errors
