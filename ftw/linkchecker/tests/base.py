from ftw.linkchecker.testing import LINKCHECKER_FUNCTIONAL
from lxml import etree
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import os.path
import transaction


class FunctionalTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
