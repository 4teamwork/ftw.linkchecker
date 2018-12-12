from setuptools import setup, find_packages
import os

version = '1.0.0.dev0'

tests_require = [
    'ftw.builder',
    'ftw.testbrowser',
    'ftw.testing',
    'plone.app.testing',
    'plone.testing',
    'pandas==0.22.0',
    'xlrd >= 0.9.0',
]

extras_require = {
    'tests': tests_require,
}


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

    install_requires=[
        'Plone',
        'setuptools',
        'ftw.upgrade',
        'xlsxwriter',
        'plone.api',
        'plone.app.relationfield',
        'plone.recipe.zope2instance',
        'plone.api'
    ],

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
