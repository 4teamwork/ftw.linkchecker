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
    def test_finds_links_in_plone_site(self, browser):
        """Checks if links in page are found and broken ones can be excluded.
        """
        self.set_up_test_environment(browser)

    @browsing
    def test_finds_broken_relations(self, browser):
        """Checks if broken relations in page are found.
        """
        self.set_up_test_environment(browser)

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
            setSite(portal)
            self.grant(portal, 'Manager')
            # add various content pages within plone site
            pages = [create(
                Builder('sl content page').titled(u'Page {}'.format(index)))
                for index in range(3)]
            urls = ['https://www.google.com', 'https://www.4teamwork.ch']
            browser.login()

            for page in pages:
                browser.visit(page)
                for index, url in enumerate(urls):
                    self.add_sl_TextBlock_having_external_link(page, url,
                                                               browser, index)

    @staticmethod
    def add_sl_TextBlock_having_external_link(current_page, link,
                                              browser, index):
        factoriesmenu.add('TextBlock', browser)
        browser.fill({
            'Title': str(index).decode("utf-8"),
            'External URL': link,
        }).save()
        browser.visit(current_page)