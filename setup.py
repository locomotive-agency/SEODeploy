from setuptools import setup
from codecs import open

exec(open('cktesting/version.py').read())

setup(
    version=__version__,
    test_suite='cktesting.tests',
)
