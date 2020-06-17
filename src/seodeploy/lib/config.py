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

from parse_it import ParseIt
from seodeploy.lib.exceptions import ModuleNotImplemented


class Config:

    """ Class for loading configuration data from Yaml settings file and module information."""

    def __init__(self, module=None, mdirs=None, cfiles=None):
        """Initialize Config Class.

        Parameters
        ----------
        module: str
            Name of module to add config data as attribute.
        mdirs: list
            Override directory to look for modules in.
        cfiles: list
            Override name of config file.

        """

        self.mdirs = (
            mdirs + ["./src/seodeploy/modules", "./seodeploy/modules", "./modules"]
            if mdirs
            else ["./src/seodeploy/modules", "./seodeploy/modules", "./modules"]
        )
        self.cfiles = (
            cfiles + ["seodeploy_config.yaml"] if cfiles else ["seodeploy_config.yaml"]
        )
        self.modules = None
        self.module = module

        super(Config, self).__init__()

        self.build()

    def _load_modules(self):
        """Load modules attribute."""

        self.modules = []
        for mdir in self.mdirs:
            try:
                self.modules.extend(
                    [
                        module
                        for module in os.listdir(mdir)
                        if os.path.isdir(os.path.join(mdir, module))
                        and not module.startswith("__")
                    ]
                )
                break
            except FileNotFoundError:
                print("Nothing found in", mdir)

    def _load_configs(self):
        """Load main configs and module configs."""

        for cfile in self.cfiles:
            try:
                parser = ParseIt(config_location=cfile, config_type_priority=["yaml"])
                config = parser.read_all_configuration_variables()

                if self.module:
                    if self.module in self.modules:
                        modules = config.pop("modules_activated")
                        self.__setattr__(self.module, Config())
                        for name, value in modules[self.module].items():
                            self.__getattribute__(self.module).__setattr__(name, value)
                    else:
                        raise ModuleNotImplemented(
                            "The module `{}` was not found in the modules directory.".format(
                                self.module
                            )
                        )

                for name, value in config.items():
                    self.__setattr__(name, value)

                break

            except FileNotFoundError:
                pass

    def build(self):
        """Build config."""
        self._load_modules()
        self._load_configs()

    def __setattr__(self, name, value):
        """Setter function for config vales."""
        super().__setattr__(name.lower(), value.strip(" /"))

    def __getattribute__(self, name):
        """getter function for config vales."""
        return super().__getattribute__(name.lower())
