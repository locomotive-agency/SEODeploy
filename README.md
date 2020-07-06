# SEODeploy: Flexible and Modular Python Library for Automating SEO Testing in Deployment Pipelines.

![SEOTesting](/docs/images/overview.png "SEO Testing Overview")


Works with:
* [Jenkins](https://www.jenkins.io/)
* [Travis CI](https://travis-ci.org/)
* [ContentKing](https://www.contentkingapp.com/)



## Overview
This library attempts to provide a flexible format to allow developers to incorporate SEO checks into development workflows.  It follows the following design constructs:

1. **Modular**: See the modules folder for examples of drop in testing using the `ModuleBase` class.  Modules dropped in here and configured in `seotesting_config.yaml` are automatically tested against sample URLs.
2. **Diff Checking**: Developers can specify in the `seotesting_config.yaml`file where they expect to see differences by ignoring checks.  Any other differences, depending on the design of the module, are diff checked across your prod and stage hosts and reported as errors.
3. **Sampled URLs**: The library supplies a sampling mechanism based on ContentKing URLs or a supplied XML sitemap URL that attempts to extract random samples in a statistically significant way.  But, developers are free to supply their own paths in the `path_samples.txt` file which are used to diff against production and staging.  One good route would be to supply a path representing each template type.
4. **Flexible**: The library contains code that is meant to be reconfigured and repurposed for individual needs.  We have tried to make classes and functions as flexible as possible, towards this end.
5. **Logging**: Error, Info, Warning notifications are logged to `seotesting.log` via included functionality.


## Modules Available
You can run as many modules as you would like.  If modules are configured in `modules_activated` of the `seodeploy_config.yaml` file, they will run.  We have provided the following examples.  ContentKing requires a subscription to [ContentKing](https://www.contentkingapp.com/).  Headless can be run on any machine capable of running Chrome.
* [ContentKing](https://locomotive-agency.github.io/SEODeploy/modules/contentking/)
* [Headless](https://locomotive-agency.github.io/SEODeploy/modules/headless/)
* [Creating Your Own](https://locomotive-agency.github.io/SEODeploy/modules/creating/)

## Getting Started
See the [docs](https://locomotive-agency.github.io/SEODeploy/) for all the information you need to get started.

!!! warning
    This library should be considered beta software and not used as a dependable
    solution without thorough testing.  Expect bugs.

## Inspiration for some parts taken from
* https://github.com/AlejandroGonzalR/jenkins-vue/tree/master/jenkins/scripts
* https://github.com/mattfair/SeleniumFactory-for-Python/blob/master/sauce_ondemand_test.py
* https://github.com/jenkins-docs/simple-python-pyinstaller-app/tree/master/jenkins
* https://github.com/PyCQA/prospector
* https://github.com/ShipChain/hydra
* https://cjolowicz.github.io/posts/hypermodern-python-03-linting/
