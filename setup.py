import os
import sys

from setuptools import find_packages
from setuptools import setup

version = '1.1.1'

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
    # later versions of pandas require python-dateutil>=2.5.0
    'pandas < 0.23.0',
    # from numpy 1.17.0 only python >= 3.5 is supported
    'numpy < 1.17.0',
    'xlrd >= 0.9.0',
    'requests',
    'xlsxwriter',
    'ftw.simplelayout [contenttypes]',
]

extras_require = {
    'tests': tests_require,
}

install_requires = [
    'Plone',
    'setuptools',
    'ftw.upgrade',
    'xlsxwriter',
    'plone.api',
    'plone.app.relationfield',
    'plone.recipe.zope2instance',
]
# python versions smaller 3.2 need
# logutils for QueueListener and QueueHandler
if sys.version_info < (3, 2):
    install_requires.extend([
        'logutils'
    ])

setup(
    name='ftw.linkchecker',
    version=version,
    description='ftw.linkchecker',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw linkchecker',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    url='https://github.com/4teamwork/ftw.linkchecker',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw'],
    include_package_data=True,
    zip_safe=False,

    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      [zopectl.command]
      check_links = ftw.linkchecker.command.checking_links:main
      """,
)
