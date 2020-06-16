
[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)


# SEODeploy: Flexible and Modular Python Library for Automating SEO Testing in Deployment Pipelines.

![SEOTesting](/docs/images/overview.png "SEO Testing Overview")


Works with:
* [Jenkins](https://www.jenkins.io/)
* [Travis CI](https://travis-ci.org/)
* [ContentKing](https://www.contentkingapp.com/)



## Quick-start Guide
This library attempts to provide a flexible format to allow developers to incorporate SEO checks into development workflows.  It follows the following design constructs:

1. **Modular**: See the modules folder for examples of drop in testing using the `ModuleBase` class.  Modules dropped in here and configured in `seotesting_config.yaml` are automatically tested against sample URLs.
2. **Diff Checking**: Developers can specify in the `seotesting_config.yaml`file where they expect to see differences by ignoring checks.  Any other differences, depending on the design of the module, are diff checked across your prod and stage hosts and reported as errors.
3. **Sampled URLs**: The library supplies a sampling mechanism based on ContentKing URLs or a supplied XML sitemap URL that attempts to extract random samples in a statisticaly signifincant way.  But, developers are free to supply their own paths in the `path_samples.txt` file which are used to diff against production and staging.  One good route would be to supply a path representing each template type.
4. **Flexible**: The library contains code that is meant to be reconfigured and repurposed for individual needs.  We have tried to make classes and functions as flexible as possible, towards this end.
5. **Logging**: Error, Info, Warning notifications are logged to `seotesting.log` via included functionality.

See the [docs](https://locomotive-agency.github.io/SEODeploy/) folder for more information.

This library should be considered Alpha software and not used as a dependable solution.  Expect bugs.


## Inspiration for some parts taken from:
* https://github.com/AlejandroGonzalR/jenkins-vue/tree/master/jenkins/scripts
* https://github.com/mattfair/SeleniumFactory-for-Python/blob/master/sauce_ondemand_test.py
* https://github.com/jenkins-docs/simple-python-pyinstaller-app/tree/master/jenkins
* https://github.com/PyCQA/prospector
* https://github.com/ShipChain/hydra
* https://cjolowicz.github.io/posts/hypermodern-python-03-linting/
