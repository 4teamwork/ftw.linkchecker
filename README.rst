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


One needs to add a config file (e.g. linkchecker_config.json) holding the sites
ids and their site administrators email addresses like:

::

    {
      "plone-site-id-one": "hugo.boss@4teamwork.com",
      "plone-site-id-one": "sec_site_admin@4teamwork.com"
    }

Json files do not have a comma at the end of the last entry!


Usage
=====

The linkchecker can be started with:

::

    bin/instance check_links --config path/to/config/file.json


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
