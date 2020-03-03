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
deployment. See non-production-info_ for more information.


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
  If set, it should be a path to a Plone container type (such as a Folder or a ``ftw.simplelayout`` file listing
  block) where the report `File` will additionally be uploaded.


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


Additional Notes
================

.. _non-production-info:

Do not run in non-production
****************************

In our setup, bin/instance is a so called ZEO client.
A ZEO client will, instead of directly opening a Data.fs,
access the ZEO server over the network.
In our setups, this is wired up via ftw-buildouts.

Now, if the ZEO server cannot be reached (not running,
network issues, misconfiguration, ...), the ZEO client will
sleep for a bit, and try to reconnect.
By default, it does this in an infinite loop and it will
try to reconnect to the mothership until the end of time.
For the regular instances (ZEP clients) running in supervisor,
this is the ideal behavior: If the ZEO server temporarily cannot
be reached, the clients will try to reconnect all by themselves.
If the ZEO comes back up again, the system will fix itself without
any need for intervention.

However, when using bin/instance from cronjobs,
this can lead to a problem. If at any given time the ZEO server
cannot be reached (for whatever reason - accidentally stopped, misconfigured,
network problems, ...), the client invoked by the cron job will attempt to
reconnect forever. Therefore that script will never terminate
(and return control to the shell). Instead it will keep running,
and the next day (or whenever the cron job gets executed the next time),
a new instance will be invoked, which will also hang.

So every night another "hanging" process that's stuck in an infinite
loop will be added. These can accumulate quickly, and lead to server-wide
resource issues. One might hit limits like max max number of open file
descriptors, number of processes per user, server memory, high load,
max number of open sockets, ... If a situation like this ever happens,
it's basically a matter of time until that entire server goes down (unless
someone recognizes the issue and fixes it).

Therefore there's at least a caveat when configuring cron jobs to run scripts
like this. It doesn't necessarily mean it shouldn't be done, but it comes with
an operational risk that's somewhat tricky to manage.
