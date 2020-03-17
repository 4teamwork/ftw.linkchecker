from ftw.linkchecker.link_accumulation import Accumulator
from ftw.linkchecker.per_site_configuration import PerSiteConfiguration
from ftw.linkchecker.tests import MultiPageTestCase
from ftw.linkchecker.tests.helpers import ConfigurationMock
from zope.component.hooks import setSite
import os


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestFindingLinksAndRelations(MultiPageTestCase):

    def test_different_emails_for_different_plone_sites(self):
        self.assertIn(
            self.portal,
            self.plone_site_objs,
            'It is expected that the first plone site is in the list of'
            'plone sites found.')

        self.assertIn(
            self.portals[1],
            self.plone_site_objs,
            'It is expected that the second plone site is in the list of'
            'plone sites found.')

    def test_email_addresses_correspond_to_correct_plone_site(self):
        setSite(self.plone_site_objs[0])
        configuration = ConfigurationMock(
            'In real I would be *args comming from argparser.')
        site = PerSiteConfiguration(self.plone_site_objs[0], configuration)

        expected = ['hugo.boss@4teamwork.ch', 'peter.wurst@4teamwork.ch']
        self.assertEqual(
                site.configuration.email, expected,
                'The emails from the example config are: {}'.format(expected))

        self.assertEqual(
            site.configuration.base_uri, 'http://example1.ch',
            'The base_uri should be http://example1.ch (from the example config.')

        setSite(self.plone_site_objs[1])
        configuration = ConfigurationMock(
            'In real I would be *args comming from argparser.')
        site = PerSiteConfiguration(self.plone_site_objs[1], configuration)

        expected = ["berta.huber@gmail.com"]
        self.assertEqual(
                site.configuration.email, expected,
                'The email from the example config is: {}'.format(expected))

        self.assertEqual(
            site.configuration.base_uri, 'http://example2.ch',
            'The base_uri should be http://example2.ch (from the example config.')

    def test_external_link(self):
        # Test 1 - External link in link field
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-0/0', self.paths_from,
            'Testing an invalid external link in IURI: We expect finding '
            '"/plone/page-0/0" in broken_relations_and_links_info because it '
            'is linking to an invalid link'
            '(http://localhost/plone/gibtsnicht).'
        )
        self.assertNotIn(
            '/plone/page-0/1', self.paths_from,
            'Testing valid external link in IURI: We expect not to find '
            '"/plone/page-0/1" in broken_relations_and_links_info'
            'because it links to a valid site'
            '(http://localhost/plone).'
        )

    def test_relation_values(self):
        # Test 2 - Relation in relation field
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-0/broken-relation', self.paths_from,
            'Testing an invalid relation in IRealtion: We expect finding '
            '"/plone/page-0/broken-relation" in broken_relations_and_links_info'
            'because it links a deleted plone site'
            '(http://localhost/plone/page-2).'
        )
        self.assertNotIn(
            '/plone/page-0/default-title', self.paths_from,
            'Testing valid relation in IRelation: We expect not to find '
            '"/plone/page-0/default-title" in broken_relations_and_links_info'
            'because it links to a valid site'
            '(http://localhost/plone/page-1).'
        )

    def test_relations_in_textarea_type1(self):
        # Test 3 - Relation in textarea (link like -> foo)
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-3/a-textblock-link-not-using-the-browser-1',
            self.paths_from,
            'Testing broken relation in textarea: We expect finding'
            '"/plone/page-3/a-textblock-link-not-using-the-browser-1" in'
            'broken_relations_and_links_info because it links to a broken'
            'relation type 1 (Idunnoexist).'
        )
        self.assertNotIn(
            '/plone/page-3/a-textblock-link-not-using-the-browser',
            self.paths_from,
            'Testing valid relation in textarea: We expect not to find'
            '"/plone/page-3/a-textblock-link-not-using-the-browser" in'
            'broken_relations_and_links_info because it links to a valid'
            'relation type 1 (content-page-on-page-3)'
        )

    def test_relations_in_textarea_type2(self):
        # Test 4 - Relation in textarea (link like -> ./foo)
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-4/a-textblock-link-not-using-the-browser-1',
            self.paths_from,
            'Testing broken relation in textarea: We expect finding'
            '"/plone/page-4/a-textblock-link-not-using-the-browser-1" in'
            'broken_relations_and_links_info because it links to a broken'
            'relation type 2 (./Icantbefound).'
        )
        self.assertNotIn(
            '/plone/page-4/a-textblock-link-not-using-the-browser',
            self.paths_from,
            'Testing valid relation in textarea: We expect not to find'
            '"/plone/page-4/a-textblock-link-not-using-the-browser" in'
            'broken_relations_and_links_info because it links to a valid'
            'relation type 2 (./content-page-on-page-4).'
        )

    def test_relations_in_textarea_type3(self):
        # Test 5 - Relation in textarea (link like -> /foo)
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-5/a-textblock-link-not-using-the-browser-1',
            self.paths_from,
            'Testing broken relation in textarea: We expect finding'
            '"/plone/page-5/a-textblock-link-not-using-the-browser-1" in'
            'broken_relations_and_links_info because it links to a broken'
            'relation type 3 (/Iwasnevercreated).'
        )
        self.assertNotIn(
            '/plone/page-5/a-textblock-link-not-using-the-browser',
            self.paths_from,
            'Testing valid relation in textarea: We expect not to find'
            '"/plone/page-5/a-textblock-link-not-using-the-browser" in'
            'broken_relations_and_links_info because it links to a valid'
            'relation type 3 (./content-page-on-page-5).'
        )

    def test_external_link_in_textarea(self):
        # Test 6 - External link in textarea (link like -> http://...)
        self.helper_function_getting_getting_link_information()
        self.assertIn(
            '/plone/page-6/a-textblock-link-not-using-the-browser-1',
            self.paths_from,
            'Testing broken link in textarea: We expect finding'
            '"/plone/page-6/a-textblock-link-not-using-the-browser-1" in'
            'broken_relations_and_links_info because it links to a broken'
            'url (http://localhost/Sadnottoexist).'
        )
        self.assertNotIn(
            '/plone/page-6/a-textblock-link-not-using-the-browser',
            self.paths_from,
            'Testing valid link in textarea: We expect not to find'
            '"/plone/page-6/a-textblock-link-not-using-the-browser" in'
            'broken_relations_and_links_info because it links to a valid'
            'url (http://localhost/plone).'
        )

    def helper_function_getting_getting_link_information(self):
        setSite(self.portal)

        configuration = ConfigurationMock(
            'In real I would be *args comming from argparser.')
        site = PerSiteConfiguration(self.plone_site_objs[0], configuration)
        accumulator = Accumulator(site)
        accumulator.discover_broken_links()
        self.paths_from = [link_obj.link_origin for link_obj in
                           accumulator.internal_broken_link_objs +
                           accumulator.external_broken_link_objs]
