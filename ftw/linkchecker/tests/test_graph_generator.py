from ftw.linkchecker.browser.dashboard import Dashboard
from ftw.linkchecker.browser.dashboard import GraphGenerator
from ftw.linkchecker.tests import FunctionalTestCase


class TestDashboardFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestDashboardFunctional, self).setUp()
        self.grant(self.portal, 'Manager')

    def test_init_graph_creator(self):
        dashboard = Dashboard(self.portal, self.request)

        self.assertTrue(
            isinstance(dashboard.graph_generator, GraphGenerator),
            'It is expected that the dashboard graph_generator is of class GraphGenerator.')
