# SEODeploy: About.

This library attempts to provide a flexible format to allow developers to incorporate SEO checks into development workflows.  It follows the following design constructs:

1. **Modular**: See the modules folder for examples of drop in testing using the `ModuleBase` class.  Modules dropped in here and configured in `seotesting_config.yaml` are automatically tested against sample URLs.
2. **Diff Checking**: Developers can specify in the `seotesting_config.yaml`file where they expect to see differences by ignoring checks.  Any other differences, depending on the design of the module, are diff checked across your prod and stage hosts and reported as errors.
3. **Sampled URLs**: The library supplies a sampling mechanism based on ContentKing URLs or a supplied XML sitemap URL that attempts to extract random samples in a statisticaly signifincant way.  But, developers are free to supply their own paths in the `path_samples.txt` file which are used to diff against production and staging.  One good route would be to supply a path representing each template type.
4. **Flexible**: The library contains code that is meant to be reconfigured and repurposed for individual needs.  We have tried to make classes and functions as flexible as possible, towards this end.
5. **Logging**: Error, Info, Warning notifications are logged to `seotesting.log` via included functionality.

## Made By
This opensource project is made possible by [LOCOMOTIVE](https://locomotive.agency/)

## Contact
If you have questions on implementation, email me at [jr.oakes@locomotive.agency](mailto:jr.oakes@locomotive.agency).

## Interested in Contributing?
Feel free to make a pull request, or email me at [jr.oakes@locomotive.agency](mailto:jr.oakes@locomotive.agency).
