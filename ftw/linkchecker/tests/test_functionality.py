from ftw.linkchecker import report_generating
from ftw.linkchecker import report_mailer
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.command import broken_link
from ftw.linkchecker.command import checking_links
from ftw.linkchecker.tests import ArchetypeFunctionalTestCase
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.linkchecker.tests import MultiPageTestCase
from ftw.linkchecker.tests.exemplar_data.exemplar_config import config_file
from ftw.testing.mailing import Mailing
from plone import api
from zope.component.hooks import setSite
import email
import os
import pandas as pd

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
        checking_links.setup_plone(self.app, self.plone_site_objs[0])
        email_address, base_uri, timeout_config = checking_links.extract_config(
            config_file)
        broken_relations_and_links_info = checking_links.get_total_fetching_time_and_broken_link_objs(
            int(timeout_config))
        self.paths_from = [list_element.link_origin for list_element in
                           broken_relations_and_links_info[1]]


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
        email_address_0, base_uri0, timeout_config0 = checking_links.extract_config(
            config_file)
        setSite(self.plone_site_objs[1])
        email_address_1, base_uri1, timeout_config1 = checking_links.extract_config(
            config_file)

        self.assertEqual(
            email_address_0,
            'hugo.boss@4teamwork.ch',
            'It is expected that the email address for page 0 is corresponding'
            'to its test site administrators email (hugo.boss@4teamwork.ch).')

        self.assertEqual(
            email_address_1,
            'berta.huber@gmail.com',
            'It is expected that the email address for page 1 is corresponding'
            'to its test site administrators email (berta.huber@gmail.com).')

        self.assertEqual(base_uri0, 'http://example1.ch',
                         'It is expected that the value was extracted from '
                         'the dictionary.')

        self.assertEqual(timeout_config0, '1',
                         'It is expected that the value was extracted from '
                         'the dictionary.')

    def helper_function_getting_getting_link_information(self):
        checking_links.setup_plone(self.app, self.plone_site_objs[0])
        email_address, base_uri, timeout_config = checking_links.extract_config(
            config_file)
        broken_relations_and_links_info = checking_links.get_total_fetching_time_and_broken_link_objs(
            int(timeout_config))
        self.paths_from = [list_element.link_origin for list_element in
                           broken_relations_and_links_info[1]]

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


class TestLinksInTextArea(FunctionalTestCase):

    def test_if_paths_from_textareas_are_correctly_joined_type_1(self):
        obj = self.textarea
        url = 'foo'
        res_path = checking_links.create_path_even_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/contentpage/foo',
            'It is expected, that paths like "foo" are appended to the parent'
            'of the textarea.')

    def test_if_paths_from_textareas_are_correctly_joined_type_2(self):
        obj = self.textarea
        url = './foo'
        res_path = checking_links.create_path_even_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/contentpage/foo',
            'It is expected, that paths like "./foo" are appended to the '
            'parent of the textarea.')

    def test_if_paths_from_textareas_are_correctly_joined_type_3(self):
        obj = self.textarea
        url = '/foo'
        res_path = checking_links.create_path_even_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/foo',
            'It is expected, that paths like "/foo" are appended to the site'
            'root.')

    def test_if_paths_from_textareas_are_correctly_joined_type_4(self):
        obj = self.textarea
        url = '../../../../foo'
        res_path = checking_links.create_path_even_there_are_parent_pointers(
            obj, url)

        self.assertEqual(
            res_path,
            '/plone/foo',
            'It is expected, that paths like "../../../../foo" (which point to'
            ' a parent further up than actually existing) are appended to the '
            'site root.')


class TestShippingInformation(FunctionalTestCase):

    def test_if_excel_generator_adds_content_correctly(self):
        """Test if an excel workbook generated by the linkchecker does not
        differ an exemplar workbook containing the expected data.
        """
        path_of_excel_workbook_exemplar = (
                CURRENT_PATH +
                '/exemplar_data/expected_excel_sheet_outcome.xlsx')
        xlsx_file = self.generate_test_data_excel_workbook()

        # import the excel workbooks as pandas dataframes
        df1 = pd.read_excel(xlsx_file)
        df2 = pd.read_excel(open(path_of_excel_workbook_exemplar, "rb"))

        diff_xlsx_files = pd.concat([df1, df2]).drop_duplicates(keep=False)

        assert df1.equals(df2), \
            "The examplar excel workbook converges from the one generated." \
            "The diff occured in following lines \n\n{}".format(
                diff_xlsx_files)

    def test_if_mail_sender_sending_mail_incl_attachement(self):
        """Test if the mail sent by linkchecker can be received correctly.
        """

        # test email variables
        email_subject = 'Linkchecker Report'
        email_message = 'Dear Site Administrator, \n\n\
            Please check out the linkchecker report attached to this mail.\n\n\
            Friendly regards,\n\
            your 4teamwork linkcheck reporter'
        receiver_email_address = 'hugo@boss.ch'
        report_path = CURRENT_PATH + \
                      '/exemplar_data/expected_excel_sheet_outcome.xlsx'
        exemplar_xlsx_file = open(report_path, "rb")

        # setUp
        Mailing(self.layer['portal']).set_up()
        portal = self.layer['portal']
        setSite(portal)

        report_mailer_instance = report_mailer.MailSender(portal)
        report_mailer_instance.send_feedback(
            email_subject, email_message, receiver_email_address,
            exemplar_xlsx_file)
        mail = Mailing(portal).pop()
        mail_obj = email.message_from_string(mail)

        self.assertEqual(
            mail_obj.get('To'), 'hugo@boss.ch',
            'The email is expected to be sent to given reveiver.')

        self.assertEqual(
            mail_obj.get_payload()[1].get_content_type(),
            'application/octet-stream',
            'The emails attachement is expected to be a binary file.')

        # tearDown
        Mailing(self.layer['portal']).tear_down()

    @staticmethod
    def generate_test_data_excel_workbook():
        example_data = broken_link.BrokenLink()
        example_data.is_internal = 'Some'
        example_data.link_origin = 'example'
        example_data.link_target = 'data'
        example_data.status_code = 'to'
        example_data.content_type = 'fill'
        example_data.response_time = 'the'
        example_data.error_message = 'sheet'
        example_data.creator = 'slowly'
        exemplar_report_data = [example_data] * 9

        base_uri = 'http://www.example_uri.com'
        file_i = report_generating.ReportCreator()
        file_i.append_report_data(report_generating.LABELS,
                                  base_uri,
                                  BOLD &
                                  CENTER &
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
        file_i.append_report_data(exemplar_report_data,
                                  base_uri,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
        file_i.add_general_autofilter()
        file_i.cell_width_autofitter()
        file_i.safe_workbook()
        xlsx_file = file_i.get_workbook()

        return xlsx_file
