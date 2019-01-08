from ftw.linkchecker.testing import LINKCHECKER_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
import transaction
from unittest2 import TestCase


class FunctionalTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, *roles):
        setRoles(self.portal, TEST_USER_ID, list(roles))
        transaction.commit()
