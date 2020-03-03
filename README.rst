ftw.linkchecker
---------------
.. contents:: Table of Contents


Introduction
============

``ftw.linkchecker`` is an add-on for Plone installations. It is designed to be run
as a cronjob regularly to find and report broken links and references within Plone sites.

How it works
****************

- The config file is inspected and the information per site configuration extracted.
- For each Plone site (whether configured or not) in the zope instance:
    - All fields possibly containing links are analysed and link/relation like
      strings are collected and stored as link objects with some additional info.
    - A check is done for each link/relation whether they are broken.
    - A report is generated in an Excel sheet.
    - The report is sent to the email addresses configured.
    - If a valid upload location is provided, the file is stored there additionally.

Important note
**************

It's important that this package isn't started by cronjob in non-production
deployments. This is because the command is started by a zope
ctl command.


Compatibility
-------------

Plone 4.3.x


Installation
============

- Add the package to your buildout configuration:

::

    [instance]
    eggs +=
        ...
        ftw.linkchecker


Configuration
=============

A JSON configuration file is required (see below for an example).
The following options can be configured in the config file per platform:

- emails of the platforms administrator (the ones who gets the report)
- base URI (domain where the platform is configured - it will be prepended to the report)
- timeout in seconds (how long the script waits for each external link before
  continuing if the page does not respond).
- upload_location can be left empty.
  It could be a path to e.g. a ``ftw.simplelayout`` file listing
  block where the report will additionally be uploaded.


::

    {
      "/plone1": {
        "email": ["first_site_admin@example.com", "first_site_keeper@example.com"],
        "base_uri": "http://example1.ch",
        "timeout_config": "1",
        "upload_location": "/content_page/my_file_listing_block"
      },
      "/folder/plone2": {
        "email": ["second_site_admin@example.com"],
        "base_uri": "http://example2.ch",
        "timeout_config": "1"
      }
    }


Usage
=====

The linkchecker can be started with the command below (`--log logpath` optional):

::

    bin/instance check_links --config path/to/config/file.json --log path/to/logfile.log


Development
===========

1. Fork this repo
2. Clone your fork
3. Shell: ``ln -s development.cfg buildout.cfg``
4. Shell: ``python bootstrap.py``
5. Shell: ``bin/buildout``

Run ``bin/test`` to test your changes.

Or start an instance by running ``bin/instance fg``.


Links
=====

- Github: https://github.com/4teamwork/ftw.linkchecker
- Issues: https://github.com/4teamwork/ftw.linkchecker/issues
- Pypi: http://pypi.python.org/pypi/ftw.linkchecker


Copyright
=========

This package is copyright by `4teamwork <http://www.4teamwork.ch/>`_.

``ftw.linkchecker`` is licensed under GNU General Public License, version 2.
