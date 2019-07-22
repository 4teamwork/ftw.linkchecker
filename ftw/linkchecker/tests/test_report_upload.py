from ftw.builder import Builder
from ftw.builder import create
from ftw.linkchecker.command import checking_links
from ftw.linkchecker.command.checking_links import get_file_name, extract_config
from ftw.linkchecker.tests import MultiPageTestCase
from ftw.linkchecker.tests.exemplar_data.exemplar_config import config_file
from ftw.linkchecker.tests.helper_generating_excel import generate_test_data_excel_workbook
from ftw.testbrowser import browsing
from zope.component.hooks import setSite
import transaction


class TestReportUploading(MultiPageTestCase):

    @browsing
    def test_report_generated_is_uploaded_to_file_listing_block_if_config_given(self, browser):
        # plone site 0 has an upload config
        setSite(self.plone_site_objs[0])
        page = create(Builder('sl content page').titled(u'Content Page'))
        file_listing_block = create(Builder('sl listingblock')
                                    .titled('File Listing Block')
                                    .within(page))
        xlsx_file = generate_test_data_excel_workbook()
        file_name = get_file_name()
        _, _, _, upload_location = extract_config(config_file)
        checking_links.upload_report_to_filelistingblock(upload_location, xlsx_file, file_name)
        transaction.commit()

        browser.visit(file_listing_block)
        node = browser.css('.linkWrapper a').first
        report_donwload_url = node.attrib.get('href', '')

        # Since we assert a link this is always lower case.
        expected_report_download_url_part = 'plone/content-page/file-listing-block/{}/download'.format(file_name).lower()

        self.assertIn(expected_report_download_url_part,
                      report_donwload_url,
                      'We expect that the report download url is built '
                      'containing the filename and context path.')
