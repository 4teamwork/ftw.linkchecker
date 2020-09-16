from ftw.linkchecker.tests import FunctionalTestCase
from ftw.linkchecker.tests.helpers import create_file_listing_block_with_report
from ftw.testbrowser import browsing


class TestDashboardFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestDashboardFunctional, self).setUp()
        self.grant(self.portal, 'Manager')

    @browsing
    def test_dashboard_content(self, browser):
        create_file_listing_block_with_report(self.portal)
        browser.login()
        browser.visit(self.portal, view='linkchecker-dashboard')

        title = browser.css('.documentFirstHeading').first.text

        self.assertEqual(
            'Linkchecker Dashboard', title,
            'It is expected that the dashboards title is Linkchecker Dashboard.')
