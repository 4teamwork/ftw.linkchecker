ftw.linkchecker
---------------
.. contents:: Table of Contents


Introduction
============

``ftw.linkchecker`` is an add-on for Plone installations. It is meant to be run
as a cronjob regularly to find broken links and references within Plone sites.

How it works
****************

- The config file is inspected and the information extracted.
- Each Plone site is dealt with separately with its info extracted.
- All fields possibly containing links are analysed and link/relation like
  strings are collected and stored as link objects with some additional info.
- A check is done for each link/relation whether they are broken.
- A report is generated in an Excel sheet.
- The report is sent to the email addresses configured.
- If a valid upload location is provided, the file is stored there additionally.

Important note
**************

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


Configuration
=============

A config file is required (there is an example in ``config.example``).
In the config file following things can be configured:

- portal path (unique identifier of the platform)
- emails of the platforms administrator (the ones who gets the report)
- base URI (domain where the platform is configured - it will be used to prepend in the report)
- timeout in seconds (how long the script waits for each external link before
  continuing if the page does not respond).
- upload_location can be left empty. It is the path to a ``ftw.simplelayout`` file listing
  block where the report will additionally be uploaded.


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
