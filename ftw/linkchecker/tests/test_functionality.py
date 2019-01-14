from AccessControl.SecurityManagement import newSecurityManager
from Acquisition import aq_parent
from ftw.builder import Builder
from ftw.builder import create
from ftw.linkchecker import report_generating
from ftw.linkchecker import report_mailer
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.command import checking_links
from ftw.linkchecker.testing import ADDITIONAL_PAGES_TO_SETUP
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.testbrowser import browsing
from ftw.testbrowser.pages import factoriesmenu
from ftw.testing.mailing import Mailing
from zope.component.hooks import setSite
import AccessControl
import email
import os
import pandas as pd
import transaction

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


class TestLinkChecker(FunctionalTestCase):

    def setUp(self):
        super(TestLinkChecker, self).setUp()
        self.portal2 = aq_parent(self.portal).get(
            ADDITIONAL_PAGES_TO_SETUP[0]['page_id'])

    @browsing
    def test_finds_broken_relations(self, browser):
        """Checks if broken relations in page are found.
        """
        self.set_up_test_environment(browser)
        site_administrator_emails = {
            "plone": "hugo.boss@4teamwork.ch",
            "plone2": "berta.huber@gmail.com"
        }
        app = self.portal.aq_parent

        plone_site_objs = checking_links.get_plone_sites_information(app)

        self.assertIn(
            self.portal,
            plone_site_objs,
            'It is expected that the first test plone site is in the list of'
            'plone sites found.')

        self.assertIn(
            self.portal2,
            plone_site_objs,
            'It is expected that the second test plone site is in the list of'
            'plone sites found.')

        plone_site_id_0 = plone_site_objs[0].getId()
        email_address_0 = site_administrator_emails[plone_site_id_0]

        plone_site_id_1 = plone_site_objs[1].getId()
        email_address_1 = site_administrator_emails[plone_site_id_1]

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

        checking_links.setup_plone(app, plone_site_objs[0])
        broken_relations_and_links_info = checking_links.get_broken_relations_and_links()

        paths_from = [list_element[1] for list_element in
                      broken_relations_and_links_info[1]]

        self.assertIn(
            '/plone/page-0/0', paths_from,
            'Testing an invalid external link in IURI: We expect finding '
            '"/plone/page-0/0" in broken_relations_and_links_info because it '
            'is linking to an invalid link'
            '(http://localhost/plone/gibtsnicht).'
        )

        self.assertIn(
            '/plone/page-0/broken-relation', paths_from,
            'Testing an invalid relation in IRealtion: We expect finding '
            '"/plone/page-0/broken-relation" in broken_relations_and_links_info'
            'because it links a deleted plone site'
            '(http://localhost/plone/page-2).'
        )

        self.assertNotIn(
            '/plone/page-0/1', paths_from,
            'Testing valid external link in IURI: We expect not to find '
            '"/plone/page-0/1" in broken_relations_and_links_info'
            'because it links to a valid site'
            '(http://localhost/plone).'
        )

        self.assertNotIn(
            '/plone/page-0/default-title', paths_from,
            'Testing valid relation in IRelation: We expect not to find '
            '"/plone/page-0/default-title" in broken_relations_and_links_info'
            'because it links to a valid site'
            '(http://localhost/plone/page-1).'
        )

        self.assertIn(
            '/plone/page-0/textblock-with-link-in-textarea-1', paths_from,
            'Testing broken link in textarea: We expect finding '
            '"/plone/page-0/textblock-with-link-in-textarea-1" in broken'
            'relations_and_links_info because it links a broken link'
            '(http://localhost:55001/plone/gibtsnicht).'
        )

        self.assertNotIn(
            '/plone/page-0/textblock-with-link-in-textarea-2', paths_from,
            'Testing valid link in textarea: We expect not to find '
            '"/plone/page-0/textblock-with-link-in-textarea-2" in broken'
            'relations_and_links_info because it links a valid link'
            '(http://localhost:55001/plone).'
        )

    def test_if_excel_generator_adds_content_correctly(self):
        """Test if an excel workbook generated by the linkchecker does not
        differ an exemplar workbook containing the expected data.
        """
        path_of_excel_workbook_generated = (
                CURRENT_PATH +
                '/exemplar_data/generator_excel_sheet_to_compare.xlsx')
        path_of_excel_workbook_exemplar = (
                CURRENT_PATH +
                '/exemplar_data/expected_excel_sheet_outcome.xlsx')

        self.generate_test_data_excel_workbook(
            path_of_excel_workbook_generated)

        # import the excel workbooks as pandas dataframes
        df1 = pd.read_excel(
            path_of_excel_workbook_generated)
        df2 = pd.read_excel(
            path_of_excel_workbook_exemplar)

        assert df1.equals(df2), \
            "The examplar excel workbook converges from the one generated."

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

        # setUp
        Mailing(self.layer['portal']).set_up()
        transaction.commit()
        portal = self.layer['portal']
        # setup plone site
        user = AccessControl.SecurityManagement.SpecialUsers.system
        user = user.__of__(portal.acl_users)
        newSecurityManager(portal, user)
        setSite(portal)

        report_mailer_instance = report_mailer.MailSender(portal)
        report_mailer_instance.send_feedback(
            email_subject, email_message, receiver_email_address, report_path)
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
    def generate_test_data_excel_workbook(path_of_excel_workbook_generated):
        exemplar_report_data = [
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
            ['Some', 'example', 'data', 'to', 'fill', 'the', 'excel', 'sheet'],
        ]

        file_i = report_generating.ReportCreator(
            path_of_excel_workbook_generated)
        file_i.append_report_data(report_generating.LABELS,
                                  BOLD &
                                  CENTER &
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
        file_i.append_report_data(exemplar_report_data,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
        file_i.add_general_autofilter()
        file_i.cell_width_autofitter()
        file_i.safe_workbook()

    def set_up_test_environment(self, browser):
        """Set up two plone sites. Both plone sites having the same content.
        Plone sites have working and broken relations and external links.
        """
        for portal in [self.portal, self.portal2]:
            broken_link = self.portal.absolute_url() + '/gibtsnicht'
            working_link = self.portal.absolute_url()

            setSite(portal)
            self.grant(portal, 'Manager')
            pages = [create(
                Builder('sl content page').titled(u'Page {}'.format(index)))
                for index in range(3)]
            browser.login()

            # add external links to pages[0]
            browser.visit(pages[0])
            for index, url in enumerate([broken_link, working_link]):
                self.add_sl_TextBlock_having_external_link(pages[0], url,
                                                           browser, index)
            # add rel-page-1 to pages[0]
            self.add_sl_TextBlock_having_relation(browser, pages[0], pages[1])
            # add rel-page-2 to pages[0]
            text_block_where_relation_will_be_destroyed = 'Broken relation'
            self.add_sl_TextBlock_having_relation(
                browser, pages[0], pages[2],
                text_block_where_relation_will_be_destroyed.decode('utf-8'))
            # delete page 2 (rel-page-2 should therefore break)
            browser.visit(pages[2])
            [browser.find('Delete').click() for i in range(2)]
            # add links to textarea of text block
            for url in [self.portal.absolute_url(),
                        self.portal.absolute_url() + '/gibtsnicht']:
                self.add_sl_TextBlock_having_link_in_textarea(browser,
                                                              pages[0], url)

    def add_sl_TextBlock_having_link_in_textarea(self, browser, page, url):
        sl_textblock_obj = create(Builder('sl textblock')
                                  .within(page)
                                  .having(current_context=False)
                                  .titled('TextBlock with link in textarea'))
        browser.visit(sl_textblock_obj, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'form.widgets.text': '<a href="{}">A banal link</a>'.format(
                url)})
        browser.find_button_by_label('Save').click()

    @staticmethod
    def add_sl_TextBlock_having_relation(browser, page, relation_obj,
                                         title=u'Default title'):
        block = create(Builder('sl textblock')
                       .within(page)
                       .having(current_context=False)
                       .titled(title))
        browser.login()
        browser.visit(block, view='edit.json')
        response = browser.json
        browser.parse(response['content'])
        browser.fill({
            'form.widgets.ITeaser.internal_link': relation_obj.absolute_url_path(), })
        browser.find_button_by_label('Save').click()

    @staticmethod
    def add_sl_TextBlock_having_external_link(current_page, link,
                                              browser, index):
        factoriesmenu.add('TextBlock', browser)
        browser.fill({
            'Title': str(index).decode("utf-8"),
            'External URL': link,
        }).save()
        browser.visit(current_page)
