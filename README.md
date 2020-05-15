
[![License](http://img.shields.io/:license-apache-blue.svg)](http://www.apache.org/licenses/LICENSE-2.0.html)


# SEOTesting: Use Content King or BYOM to automate CI/CD testing.

![SEOTesting](https://raw.githubusercontent.com/jroakes/SEOTesting/master/docs/overview.png "SEO Testing Overview")


Works with:
* [Jenkins](https://www.jenkins.io/)
* [Travis CI](https://travis-ci.org/)
* [ContentKing](https://www.contentkingapp.com/)



## Quick-start Guide
This library attemtps to provide a flexible format for allowing developers to incorporate SEO checks into development workflows.  It follows the following design constructs:

1. **Modular**: See the modules folder for examples of drop in testing using the `ModuleBase` class.  Modules dropped in here and configured in `seotesting_config.yaml` are automatically tested against sample URLs.
2. **Diff Checking**: Developers can specify in the `seotesting_config.yaml` where they expect to see differences by ignoring.  Any other differences, depending on the design of the module diff checked across your prod and stage host and reported as errors.
3. **Sampled URLs**: The library supplies a sampling mechanism based on ContentKing URLs or a supplied XML sitemap URL that attempts to extract random samples in a statisticaly signifincant way.  But, developers are free to supply their own paths in the `path_samples.txt` file which are used to diff against production and staging.  One good route would be to supply a path representing each template type.
4. **Flexible**: The library contains code that is meant to be reconfigured and repurposed for individual needs.  We have tried to make classes and functions as flexible as possible, towards this end.
5. **Logging**: Error, Info, Warning notifications are logged to `seotesting.log` via included functionality.

See the docs folder for more information. [Coming Soon]

See [TODO](TODO.md) for what is currently in process.

This libray should be considered Alpha software and not used as a dependable solution.  Expect bugs.



# Developer Instructions

### Install
```
Current:
pip install https://github.com/jroakes/SEOTesting.git

Future:
pip install seotesting

```


### Configure client and run node

1. Create samples paths file

      Using a ContentKing website:

    `seotesting sample -siteid 12346`

      Using a XML sitemap or sitemap index file:

    `seotesting sample --sitemap_url https://locomotive.agency/sitemap_index.xml`

2. Compare Staging and Production based on `seotesting_config.yaml` configuration and `sample_paths.txt`.

    `seotesting execute`



## General Installation and Development Guidelines

### Installation

```
$ conda create --name seotesting

$ pip install https://github.com/jroakes/SEOTesting.git
```

OR:

```
$ git clone https://github.com/jroakes/SEOTesting.git

$ cd SEOTesting

$ pip install -r requirements.txt

$ pip install setup.py
```





## Inspiration for some parts taken from:
* https://github.com/AlejandroGonzalR/jenkins-vue/tree/master/jenkins/scripts
* https://github.com/mattfair/SeleniumFactory-for-Python/blob/master/sauce_ondemand_test.py
* https://github.com/jenkins-docs/simple-python-pyinstaller-app/tree/master/jenkins
* https://github.com/PyCQA/prospector
* https://github.com/ShipChain/hydra
