from ftw.builder import Builder
from ftw.builder import create
from ftw.linkchecker.link_accumulation import Accumulator
from ftw.linkchecker.per_site_configuration import PerSiteConfiguration
from ftw.linkchecker.report_generating import ReportHandler
from ftw.linkchecker.tests import MultiPageTestCase
from ftw.linkchecker.tests.helpers import ConfigurationMock
from ftw.testbrowser import browsing
from zope.component.hooks import setSite
import transaction


class TestReportUploading(MultiPageTestCase):

    @browsing
    def test_report_generated_is_uploaded_to_file_listing_block_if_config(
            self, browser):
        # plone site 0 has an upload config
        setSite(self.plone_site_objs[0])
        page = create(Builder('sl content page').titled(u'Content Page'))
        file_listing_block = create(Builder('sl listingblock')
                                    .titled('File Listing Block')
                                    .within(page))

        # Run linchecker features needed for getting a report
        configuration = ConfigurationMock(
                'In real I would be *args comming from argparser.')
        site = PerSiteConfiguration(self.plone_site_objs[0], configuration)
        accumulator = Accumulator(site)
        accumulator.discover_broken_links()
        report_handler = ReportHandler(site, accumulator)
        report_handler.upload_report()
        transaction.commit()

        browser.visit(file_listing_block)
        node = browser.css('.linkWrapper a').first
        report_donwload_url = node.attrib.get('href', '')

        # Since we assert a link this is always lower case.
        expected_report_download_url_part = (
            'plone/content-page/file-listing-block/{}/download'.format(
                report_handler._file_name).lower())

        self.assertIn(expected_report_download_url_part,
                      report_donwload_url,
                      'We expect that the report download url is built '
                      'containing the filename and context path.')
