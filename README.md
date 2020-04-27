
[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)


# CKTesting: Use Content King to automate CI/CD testing.

Works with:
* Jenkins
* Travis CI



## Quick-start Guide
See the docs folder.



# Developer Instructions

### Install
```
pip install cktesting
```


### Configure client and run node

1. Create samples paths file
`cktesting sample -siteid 12346`

2. Compare Staging and Production
`cktesting test`



## General Installation and Development Guidelines

### Installation

```
$ pip install -r requirements.txt

$ pip install setup.py
```


#### Environment Setup

The following demonstrates setting up and working with a development environment:

```
### create a virtualenv for development

$ make virtualenv

$ source env/bin/activate


### run cli application

$ cktesting --help


### run pytest / coverage

$ make test
```
