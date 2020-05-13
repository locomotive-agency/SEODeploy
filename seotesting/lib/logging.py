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

import logging
from logging import DEBUG, Formatter, INFO, getLogger

from .config import Config

config = Config()




# file output
file_handler = logging.FileHandler(filename=config.LOG_FILE or 'seotesting.error.log')

file_handler.setFormatter(Formatter('%(asctime)s [%(levelname)s]'
                                    '  %(name)s,%(lineno)s  %(message)s'))
file_handler.setLevel(DEBUG)

# console output
console_handler = logging.StreamHandler()
console_handler.setLevel(INFO)
console_handler.setFormatter(Formatter('%(message)s'))


sdct_logger = getLogger(config.SEOTESTING_NAME)

# add handlers
sdct_logger.addHandler(console_handler)
sdct_logger.addHandler(file_handler)
sdct_logger.setLevel(DEBUG)

logging.captureWarnings(True)


def get_logger(log_name, level=DEBUG):
    """
    :param level:   CRITICAL = 50
                    ERROR = 40
                    WARNING = 30
                    INFO = 20
                    DEBUG = 10
                    NOTSET = 0
    :type log_name: str
    :type level: int
    """
    module_logger = sdct_logger.getChild(log_name)
    if level:
        module_logger.setLevel(level)
    return module_logger
