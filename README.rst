ftw.linkchecker
---------------
.. contents:: Table of Contents


Introduction
============

### INTRODUCTION ###

It's important, that this package isn't started by conjob in non productive
deployments. This is due to the fact, that the command is started by a zope
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


One needs to add a config file (e.g. linkchecker_config.json) holding:

- portal path (unique identifier of the platform)
- emails of the platforms administrator (the ones who gets the report)
- base URI (domain where the platform is configured)
- timeout in seconds (how long the script waits for each external link before
  continuing if the page does not respond).
- upload_location can be left empty. It is the path to a file listing
  block where the report will be uploaded.

::

    {
      "/portal/path-one": {
        "email": ["first_site_admin@example.com", "first_site_keeper@example.com"],
        "base_uri": "http://example1.ch",
        "timeout_config": "1",
        "upload_location": "/content_page/my_file_listing_block"
      },
      "/portal/path-two": {
        "email": ["second_site_admin@example.com"],
        "base_uri": "http://example2.ch",
        "timeout_config": "1"
      }
    }



Usage
=====

The linkchecker can be started with (`--log logpath` optional):

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
