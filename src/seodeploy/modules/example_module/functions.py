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


from seodeploy.lib.logging import get_logger
from seodeploy.lib.helpers import group_batcher, mp_list_map, process_page_data  # noqa
from seodeploy.modules.example_module.exceptions import ExampleExceptions  # noqa


_LOG = get_logger(__name__)


def run_example_module(sample_paths, config):  # noqa
    """Sample function for Module.

    Parameters
    ----------
    sample_paths: list
        List of paths.
    config: Config
        Module config class.

    Returns
    -------
    dict
        Page Data dict.
    """

    # Do stuff.....

    # Log Error.
    # _LOG.error('This is an error.')

    # Log Info
    # _LOG.info('This is information.')

    # This batches URLs based of config-set batch size.
    # batches = group_batcher(sample_paths, list, config.headless.BATCH_SIZE, fill=None)

    # Multiprocessing function.  Based on config.max_threads.
    # mp_list_map(
    #     batch, _render_paths, config=config, host=config.headless.STAGE_HOST
    # )

    # Review for Errors and process into dictionary
    # page_data = process_page_data(
    #     sample_paths, prod_result, stage_result, config.example
    # )

    pass  # noqa
