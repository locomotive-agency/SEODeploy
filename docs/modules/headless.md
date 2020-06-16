# SEODeploy: Guide for the Headless Module.


## About Headless

The Headless module uses Google Chrome in Headless mode to render URLs and extract content, for comparison, from the rendered DOM.  It also allows for the collection of timing and other performance metrics, like coverage data, for tested URLs.

## Usage
To use the module requires a computer running Python v3.7 (tested) and enough space and memory to run Chromium (~150MB space, 8GB memory suggested).

### Configuring Headless Module
To activate the Headless Module, the following YAML code block should be nested under `modules_activated` in your `seotesting_config.yaml` file.

```
headless:
  batch_size: 5
  pyppeteer_chromium_revision: 769582
  network_preset: Regular3G
  prod_host: https://locomotive.agency
  stage_host: https://stg.locomotive.agency
  stage_auth_user: user
  stage_auth_pass: pass

  user_agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36

  replace_staging_host: True

  ignore:
    content:
        canonical: False
        robots: False
        title: False
        meta_description: False
        h1: False
        h2: False
        links: True
        images: True
        schema: False

    performance:
        nodes: 0.20
        resources: 0.20
        layout_duration: 0.20
        recalc_style_duration: 0.20
        script_duration: 0.20
        v8_compile_duration: 0.20
        task_duration: 0.20
        task_other_duration: 0.20
        thread_time: 0.20
        jd_heap_used_size: 0.20
        js_heap_total_size: 0.20
        time_to_first_byte: 0.20
        first_paint: 0.20
        first_contentful_paint: 0.20
        largest_contentful_paint: 0.20
        time_to_interactive: 0.20
        dom_content_loaded: 0.20
        dom_complete: 0.20
        cumulative_layout_shift: 0.20

    coverage:
      summary:
        total_unused: 0.20
        total_bytes: 0.20
        unused_pc: 0.20

      css:
        total_unused: 0.20
        total_bytes: 0.20
        unused_pc: 0.20

      js:
        total_unused: 0.20
        total_bytes: 0.20
        unused_pc: 0.20
```



#### Configurable Items

**Chromium Settings:**

These are settings for configuring Chromium and how it crawls your sites.

* **batch_size**: (int) Number of pages to check in each batch.
* **pyppeteer_chromium_revision**: (str) Chromium Version.  Versions can be found [here](https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html).
* **network_preset**: (str) Network presets for Chromium. Controls upload and download speed, as well as latency.  Possible values: `GPRS`, `Regular2G`, `Good2G`, `Regular3G`, `Good3G`, `Regular4G`, `DSL`, `WiFi`.

* **prod_host**: (str) URL of production host (eg. https://locomotive.agency)
* **stage_host**: (str) URL of staging host (eg. https://stg.locomotive.agency)

* **stage_auth_user**: (str) Username to bypass Authentication on Staging website.
* **stage_auth_pass**: (str) Password to bypass Authentication on Staging website.

* **user_agent**: (str) User Agent to crawl as.  This is helpful to bypass security or compression/caching of CDNs on production website.

* **replace_staging_host**: (bool) Whether to search/replace staging host with production host, in staging HTML.


**Comparison Settings**:

These are settings that affect what is compared between your production and staging URLs.

* **content**: Content is extracted content, like H1s, H2s, and SEO Meta data for each URL.  Set `True` or `False`
* **performance**: Performace data collected for each URL.  Includes timing and select CDP Performance API data.  Set `True`, `False`, or <float>.  <float> values allow you to report on numeric changes greater than the percent supplied.  e.g. a value of `0.20` would only report changes that are greater than 20%.
* **coverage**: Coverage is JS and CSS coverage data collected via the CDP Coverage API. Set `True`, `False`, or <float>.  <float> values allow you to report on numeric changes greater than the percent supplied.  e.g. a value of `0.20` would only report changes that are greater than 20%.

### Running
Once configured, the Headless module will run against all sample paths on Staging and Production, comparing items not excluded in the `Comparison Settings` above.
