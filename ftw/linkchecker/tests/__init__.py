from ftw.linkchecker.testing import LINKCHECKER_FUNCTIONAL
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unittest2 import TestCase
import transaction


class FunctionalTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def grant(self, portal=None, *roles):
        if isinstance(portal, str):
            roles.append(portal)
            portal = self.portal
        elif isinstance(portal, list) or isinstance(portal, tuple):
            roles = list(portal)
            portal = self.portal
        else:
            portal = portal or self.portal

        setRoles(portal, TEST_USER_ID, list(roles))
        transaction.commit()
