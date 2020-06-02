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

import json
from datetime import datetime
import pandas as pd

from seodeploy.lib.modules import ModuleConfig
from seodeploy.lib.sampling import get_sample_paths
from seodeploy.lib.logging import get_logger
from seodeploy.lib.config import Config

_LOG = get_logger(__name__)


class SEOTesting:
    def __init__(self, config=None):
        """ SEOTesting Class: Base Class for SEODeploy"""
        self.config = config or Config()
        self.messages = []
        self.module_config = ModuleConfig(self.config)

        self.samples = None
        self.modules = None
        self.summary = None
        self.passing = True

    def execute(self, samples_filename=None):

        self.summary = {"started": str(datetime.now())}

        # Get Sample Paths
        self.samples = get_sample_paths(self.config, filename=samples_filename)
        self.summary.update({"samples": len(self.samples)})

        # get Modules
        self.modules = self.module_config.module_names
        self.summary.update({"modules": ",".join(self.modules)})

        for active_module in self.module_config.active_modules:

            module = self.module_config.active_modules[active_module].SEOTestingModule()

            errors = module.run(self.samples)

            self.update_messages(module.messages)
            self.update_passing(module.passing)

            self.summary.update(
                {"{} passing: ".format(module.modulename): module.passing}
            )
            self.summary.update({"{} errors: ".format(module.modulename): len(errors)})

        self.get_messages().to_csv("output.csv", index=False)

        self.print_summary()

        return self.passing

    def update_messages(self, messages):
        self.messages.extend(messages)

    def update_passing(self, passing):
        self.passing = False if not passing and self.passing else self.passing

    def get_messages(self):
        return pd.DataFrame(self.messages)

    def print_summary(self):
        print("Run CSV saved to:", "output.csv")
        print()
        print("Run Summary")
        print(json.dumps(self.summary, indent=2))
