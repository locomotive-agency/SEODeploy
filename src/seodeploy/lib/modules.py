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
from functools import reduce

from .config import Config
from .comparison import CompareDiffs
from .helpers import to_dot, dot_get
from .logging import get_logger

from .exceptions import ModuleNotImplemented, IncorrectConfigException

_LOG = get_logger(__name__)


class ModuleBase:
    """Base Module class."""

    def __init__(self, config=None, sample_paths=None, exclusions=None):
        self.messages = None
        self.errors = None
        self.passing = None
        self.mappings = None
        self.modulename = None
        self.sample_paths = sample_paths
        self.exclusions = exclusions
        self.config = config or Config()


    def run_diffs(self, page_data):
        """Run diffs across dictionary of path, stage, and prod data.

        Parameters
        -----------------
        page_data: {'<path>':{'prod': <prod url data>, 'stage': <stage url data>, 'error': error},
                   ...
                   }
        """

        if self.modulename and self.exclusions:

            self.errors = []
            self.mappings = to_dot(self.exclusions)

            diffmodule = CompareDiffs()



            # Iterate paths
            for path, path_data in page_data.items():

                error = path_data["error"]

                if error:
                    self.errors.append({"path": path, "error": error})

                else:
                    for mapping in self.mappings:
                        try:
                            self.iter_mappings(path, diffmodule, mapping, path_data)
                        except IncorrectConfigException as e:
                            self.errors.append({"path": path, "error": str(e)})
                            break

            return diffmodule.get_diffs()

        raise NotImplementedError("This module cannot be called directly.")

    def _iter_mappings(self, path, diffmodule, mapping, path_data):
        """Iterates mappings to execute comparisions."""

        item = mapping
        exc = dot_get(item, self.exclusions)
        d1 = dot_get(item, path_data["prod"])
        d2 = dot_get(item, path_data["stage"])

        if exc is not None and d1 and d2:

            if isinstance(exc, bool):
                if not exc:
                    diffmodule.compare(path, item, d1, d2, tolerance=None)
            elif isinstance(exc, float):
                diffmodule.compare(path, item, d1, d2, tolerance=exc)
            else:
                raise IncorrectConfigException(
                    "Config ignore values must be `bool` or `float`"
                )

        else:
            raise IncorrectConfigException("Config mapping data is not correct.")

    def prepare_messages(self, diffs):
        """ Prepares Diff data as consistent messages.

        Data should be in format of
            [{'path': <str>, 'diffs': <list>}, ...]

        Output in format:
            [{'module': <str>, 'path': <str>, 'diffs': [list]}, ...]
        """
        messages = []

        for item in diffs:

            path = item["path"]
            item_diffs = item["diffs"]

            for item_diff in item_diffs:

                # make sure all values are strings.
                item_diff = {k: str(v) for k, v in item_diff.items()}.update(
                    {"module": self.modulename, "path": path}
                )

                messages.append(item_diff)

        self.messages = messages

        return messages

    def run(self, sample_paths):
        raise NotImplementedError


class ModuleConfig:
    """Builds modules and contains module information."""

    def __init__(self, config=None, mdirs=None):

        self.config = config or Config()
        self.mdirs = mdirs + ["modules"] if mdirs else ["modules"]
        self.data = self._get_module_data()

        self.module_paths = self._get_module_paths(self.data)
        self.module_names = self._get_module_names(self.data)

        self.active_modules = {}

        self._build_modules()

    def _build_modules(self):

        sys.path.append(self.module_path)

        for k, v in self.data.items():
            if v["is_config"]:
                self.active_modules[k] = importlib.import_module(k)

    def _is_confugured(self, module):

        if hasattr(self.config, "modules_activated"):
            return module in list(self.config.modules_activated.keys())
        return False

    def _get_module_data(self):

        for mdir in self.mdirs:

            mdir = os.path.join(os.path.dirname(__file__), "..", mdir)

            if not os.path.isdir(mdir):
                continue

            break

        else:
            raise ModuleNotImplemented(
                "Modules directory not found in: {}".format(",".join(self.mdirs))
            )

        self.module_path = mdir

        return {
            f.name: {
                "name": f.name,
                "path": f.path,
                "mdir": mdir,
                "is_config": self._is_confugured(f.name),
            }
            for f in os.scandir(mdir)
            if f.is_dir()
        }

    @staticmethod
    def _get_module_names(data):
        return [k for k, v in data.items() if v["is_config"]]

    @staticmethod
    def _get_module_paths(data):
        return [v["path"] for k, v in data.items() if v["is_config"]]
