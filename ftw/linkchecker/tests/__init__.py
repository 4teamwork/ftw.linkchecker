from Acquisition import aq_parent
from ftw.linkchecker.command import checking_links
from ftw.linkchecker.test_setup import add_archetype_link_to_plone_site
from ftw.linkchecker.test_setup import add_textarea_to_page
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
        self.textarea = add_textarea_to_page(self.portal)

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


class ArchetypeFunctionalTestCase(TestCase):
    layer = LINKCHECKER_FUNCTIONAL

    def setUp(self):
        self.request = self.layer['request']
        self.portal = self.layer['portal']
        plonefti = self.portal.portal_types.get('Plone Site')
        addable_types = list(plonefti.allowed_content_types) + ['Link']
        plonefti.allowed_content_types = tuple(addable_types)
        add_archetype_link_to_plone_site(self.portal)

        self.app = self.portal.aq_parent
        self.plone_site_objs = list(checking_links._get_plone_sites(self.app))

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

        self.app = self.portal.aq_parent
        self.plone_site_objs = list(checking_links._get_plone_sites(self.app))

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
