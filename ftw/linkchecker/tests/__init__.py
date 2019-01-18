from Acquisition import aq_parent
from ftw.linkchecker.test_setup import set_up_test_environment
from ftw.linkchecker.testing import ADDITIONAL_PAGES_TO_SETUP
from ftw.linkchecker.testing import LINKCHECKER_FUNCTIONAL
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from unittest2 import TestCase
import transaction


class FunctionalTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']

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


class MultiPageTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']

        # create list of all pages
        self.portals = [self.portal]
        for additional_page in ADDITIONAL_PAGES_TO_SETUP:
            self.portals.append(aq_parent(self.portal).get(
                additional_page['page_id']))

        for portal in self.portals:
            set_up_test_environment(portal)

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
