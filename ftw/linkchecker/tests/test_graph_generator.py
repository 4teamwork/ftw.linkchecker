from ftw.linkchecker.browser.dashboard import Dashboard
from ftw.linkchecker.browser.dashboard import GraphGenerator
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.linkchecker.tests.helpers import create_file_listing_block_with_report


class TestGraphGeneratorFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestGraphGeneratorFunctional, self).setUp()
        self.grant(self.portal, 'Manager')

    def test_init_graph_creator(self):
        dashboard = Dashboard(self.portal, self.request)

        self.assertTrue(
            isinstance(dashboard.graph_generator, GraphGenerator),
            'It is expected that the dashboard graph_generator is of class GraphGenerator.')

    def test_plotting_status_graph(self):
        create_file_listing_block_with_report(self.portal)
        dashboard = Dashboard(self.portal, self.request)

        actual = dashboard.graph_generator.get_status_plot()
        expected = '<img src="data:image/png;base64, iVBORw0KGgoAAAAN'

        self.assertIn(
            expected, actual,
            'The response should be an image tag containing a base64 value.')

    def test_plotting_creator_graph(self):
        create_file_listing_block_with_report(self.portal)
        dashboard = Dashboard(self.portal, self.request)

        actual = dashboard.graph_generator.get_status_plot()
        expected = '<img src="data:image/png;base64, iVBORw0KGgoAAAAN'

        self.assertIn(
            expected, actual,
            'The response should be an image tag containing a base64 value.')

    def test_plotting_state_graph(self):
        create_file_listing_block_with_report(self.portal)
        dashboard = Dashboard(self.portal, self.request)

        actual = dashboard.graph_generator.get_status_plot()
        expected = '<img src="data:image/png;base64, iVBORw0KGgoAAAAN'

        self.assertIn(
            expected, actual,
            'The response should be an image tag containing a base64 value.')

    def test_plotting_history_graph(self):
        create_file_listing_block_with_report(self.portal, upload_two=True)
        dashboard = Dashboard(self.portal, self.request)

        actual = dashboard.graph_generator.get_history_plot()
        expected = '<img src="data:image/png;base64, iVBORw0KGgoAAAAN'

        self.assertIn(
            expected, actual,
            'The response should be an image tag containing a base64 value.')
