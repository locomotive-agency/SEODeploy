# SEODeploy: About

SEODeploy is a labor of love which attempts to solve a common issue with deployment processes: SEO Error Checking.  Often small mistakes, such as a changed canonical pattern, can have far-reaching traffic implications when deployed to production.  Further, a lot of time can be lost by having team members manually check pages for issues and some SEO issues are easy to miss.  By bringing SEO teams and development teams together to decide on the **correct** items to validate, and providing an automated way of including those checks, we hope to provide a tool which saves time and creates more consistency in your CI/CD workflows.

We decided to integrate ContentKing because it really does allow for fuller end-to-end confidence. You can integrate our tool to catch mistakes on staging, but even if a mistake passes to production, ContentKing is there to let you know immediately, so you can quickly roll back changes.

## Why Python?
We know that items like Puppeteer run more naturally on Node and Python is in no way the most efficient language. A few of the reasons we still thought Python would be the correct choice:

1. [Pyppeteer](https://github.com/pyppeteer/pyppeteer) is available for Headless Chrome support, which tries to mirror the functionality of Puppeteer, as closely as possible.
2. Python is a popular, and growing language, so finding developers is easier than others.
3. The upside on creating additional modules for link analysis, NLP, extraction, anomaly detection, etc, with popular, and trusted available libraries, was a clear win.
4. Python is supported in most cloud function environments, so running at the location of your choice is an option.
5. Python can run asynchronously or synchronously.
6. The tool doesn't care what language your site is developed in.  Only what is outputted to Staging and Production pages.


## Made By
This opensource project is developed by [LOCOMOTIVE](https://locomotive.agency/), a Technical SEO Agency.

## Contact
If you have questions on implementation, email me at [jr.oakes@locomotive.agency](mailto:jr.oakes@locomotive.agency).

## Interested in Contributing?
Feel free to make a pull request, or email me at [jr.oakes@locomotive.agency](mailto:jr.oakes@locomotive.agency).
