from ftw.linkchecker.accumulator import Accumulator
from ftw.linkchecker.per_site_configuration import PerSiteConfiguration
from ftw.linkchecker.tests import ArchetypeFunctionalTestCase
from ftw.linkchecker.tests.helpers import ConfigurationMock
from zope.component.hooks import setSite
import os


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestArchetypeLink(ArchetypeFunctionalTestCase):

    def test_external_link(self):
        self.helper_check_links()

        self.assertIn('/plone/ftw-simplelayout-contentpage/archetype-link-1',
                      self.paths_from,
                      'Testing a broken external archetype link: It is'
                      'expected that we find archetype-link-1 in the broken'
                      'link list because it is pointing to '
                      '"http://localhost:55001/plone/ImWearingAnInvisibilityCloak".')

        self.assertNotIn('/plone/ftw-simplelayout-contentpage/archetype-link',
                         self.paths_from,
                         'Testing a working external archetype link: It is'
                         'expected that we don\'t find archetype-link in the '
                         'broken link list because it is pointing to '
                         '"http://localhost:55001/plone".')

    def test_relation(self):
        self.helper_check_links()

        self.assertIn('/plone/ftw-simplelayout-contentpage/archetype-link-3',
                      self.paths_from,
                      'Testing a broken archetype relation: It is expected '
                      'that we find archetype-link-3 in the broken link list '
                      'because it is pointing to a deleted object.')

        self.assertNotIn(
            '/plone/ftw-simplelayout-contentpage/archetype-link-2',
            self.paths_from,
            'Testing a valid archetype relation: It is expected '
            'that we don\'t find archetype-link-2 in the broken '
            'link list because it is pointing to a valid object.')

    def helper_check_links(self):
        setSite(self.portal)

        configuration = ConfigurationMock(
            'In real I would be *args comming from argparser.')
        site = PerSiteConfiguration(self.plone_site_objs[0], configuration)
        accumulator = Accumulator(site)
        accumulator.discover_broken_links()
        self.paths_from = [link_obj.link_origin for link_obj in
                           accumulator.internal_broken_link_objs +
                           accumulator.external_broken_link_objs]
