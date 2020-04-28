from ftw.linkchecker.tests import FunctionalTestCase
from ftw.testbrowser import browsing


class TestDashboardFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestDashboardFunctional, self).setUp()
        self.grant(self.portal, 'Manager')

    @browsing
    def test_dashboard_content(self, browser):
        browser.login()
        browser.visit(self.portal, view='linkchecker-dashboard')

        title = browser.css('.documentFirstHeading').first.text
        content = browser.css('#content-core').first.text

        self.assertEqual(
            'Linkchecker Dashboard', title,
            'It is expected that the dashboards title is Linkchecker Dashboard.')

        self.assertIn(
            'Lorem ipsum', content,
            'It is expected that Lorem ipsum is in the content.')