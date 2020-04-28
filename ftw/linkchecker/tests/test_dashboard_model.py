from ftw.linkchecker.browser.dashboard import Dashboard
from ftw.linkchecker.tests import FunctionalTestCase


class TestDashboardFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestDashboardFunctional, self).setUp()
        self.grant(self.portal, 'Manager')

    def test_read_path_from_registry(self):

        dashboard = Dashboard(self.portal, self.request)

        self.assertEqual(
            u'linkchecker/reports', dashboard.dashboard_model._get_report_path(),
            'It is expected to get the path configured in the registry.')

    def test_write_and_read_annotation(self):

        dashboard = Dashboard(self.portal, self.request)
        expected = {'data': 'example data'}

        # set annotation to expected
        dashboard.dashboard_model._set_annotation(expected)

        self.assertEqual(
            expected, dashboard.dashboard_model._get_annotation(),
            'It is expected that the annotation value can be set and get.')

