# SEODeploy: Creating New Modules.

## About Example Module

We have provided an example module at `/modules/example_module` to show you how to create your own custom testing tool.

## Usage
Overview of creating your own module for SEODeploy.

### Module Structure

    /modules/example_module/
        /modules/example_module/__init__.py
        /modules/example_module/functions.py
        /modules/example_module/exceptions.py


### Files
* **__init__.py**: Contains the class used to activate and run the module.
* **functions.py**: Should contain any custom functions for your module.
* **exceptions.py**: Should contain any custom exceptions for your module.


### Module Class Flow
The flow of creating your own module is outlined below.

1. The `modulename` should be defined in the SEOTestingModule class. e.g. `self.modulename = "example_module"`
2. The `modulename` should be the same as the module folder name, and name of configuration section of `seotesting_config.yaml`.
3. Sample paths are passed to the `run` method of your module's class in `__init__.py`.
4. There should be a function in `functions.py` that accepts `sample_paths` and `config` parameters, and returns data formatted with the `seodeploy.lib.process_page_data` function.
5. `page_data` is passed to the `self.run_diffs` method and diffs are calculated.
6. `diffs` are passed to the `self.prepare_messages` method and issue messages are generated.
7. `self.messages` and `errors` are returned back to the main SEODeploy tool.
8. If `len(messages) > 0` or if `len(errors) > 0` then the tool fails.


### Available Helper Functions

The `seodeploy.lib.helpers` module contains the following functions which help maintain consistency in your module's functions.

#### group_batcher

  Given and iterator, returns batched results based on count.

    Given and iterator, returns batched results based on count.

    Call: group_batcher(iterator, result, count, fill=0)

    Parameters
    ----------
    iterator: list or tuple
        Iterable object
    result: type
        The `type` of the results to be returned. `list` or `set`
    count: int
        How many in each Group.
    fill: str, int, float, or None
        Fill overflow with this value. If None, no fill is performed.

    Returns
    -------
    Generator

#### mp_list_map

  Applies a function to a list by multiprocessing, maybe.

    Applies a function to a list by multiprocessing.

    Call: mp_list_map(lst, fnc, \*\*kwargs)

    Uses `max_threads` from `seotesting_config.yaml` to determine whether to apply
    function by multiprocessing.  if max_threads > 1 , then multiprocessing is used.

    Parameters
    ----------
    lst: list
        Iterable object
    fnc: function
        A function to map to all list values.
    kwargs: dict
        keyword parameters to supply to your function.

    Returns
    -------
    list
        List of data updated by function.


#### process_page_data

  Reviews the returned results for errors and formats result.

    Reviews the returned results for errors and formats result.

    Call: process_page_data(sample_paths, prod_result, stage_result, module_config)

    Parameters
    ----------
    sample_paths: list
        List of Paths.
    prod_results: list
        List of prod data dictionaries.
        Fmt: [{'path': '/', 'page_data':{'content': {'h1': 'heading'}},
               'error': None}, ...]
    stage_result: list
        List of stage data dictionaries.
        Fmt: [{'path': '/', 'page_data':{'content': {'h1': 'heading'}},
               'error': None}, ...]
    module_config: Config
        Module config.

    Returns
    -------
    dict
        Dictionary in format:
        {'<path>':{'prod': <prod url data>, 'stage': <stage url data>,
        'error': error},
        ...
        }
    """

### Configuration

#### Main Config Data

  Here is an example base configuration for your module in `seotesting_config.yaml`. All given parameters below are required.

    modules_activated:

      example_module:
        batch_size: 5
        prod_host: https://locomotive.agency
        stage_host: https://stg.locomotive.agency
        replace_staging_host: True

        ignore:
          <this should match the structure of dictionary data
           provided to the `process_page_data` function>


  Any new parameters you add to your module's config are available to the config class.

  Example:

    # seotesting_config.yaml
    example_module:
        custom_parameter: 1

    # /modules/example_module/functions.py
    config = Config(module='example_module')
    assert config.example_module.custom_parameter == 1

#### Ignore Config Data

  The `ignore` section of your module's config information should match the `page_data`
  dictionary that is sent to `process_page_data` in the `prod_results` and `stage_result` parameters.

  Example:

    page_data = {'content': {'h1': 'main heading',
                             'h2': 'sub-heading'},
                 'other': {'something': 'value'}
                }

    example_module:
      ...
      ignore:
        content:
          h1: False
          h2: False
        other:
          something: True



### Diff Checking

Diff checking is done automatically.  Any data you supply in `page_data` for each key is tested based on its specific type.

Supports: Strings, Dicts, Lists, Sets, Float, and Ints.
