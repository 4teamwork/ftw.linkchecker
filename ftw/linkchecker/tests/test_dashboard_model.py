from ftw.linkchecker.browser.dashboard import Dashboard
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.linkchecker.tests.exemplar_data.annotation_asset import ANNOTATION_ASSET
from ftw.linkchecker.tests.helpers import create_file_listing_block_with_report
import numpy as np
import pandas as pd


class TestDashboardModelFunctional(FunctionalTestCase):

    def setUp(self):
        super(TestDashboardModelFunctional, self).setUp()
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

    def test_first_time_loading_page_with_no_persisted_data_no_report(self):
        dashboard = Dashboard(self.portal, self.request)
        df = dashboard.dashboard_model.data

        self.assertTrue(
            isinstance(df, pd.DataFrame),
            'For consistency reasons "no data" should still return a DataFrame.')

    def test_first_time_loading_page_with_no_persisted_data(self):
        create_file_listing_block_with_report(self.portal)
        dashboard = Dashboard(self.portal, self.request)
        df = dashboard.dashboard_model.data

        self.assertTrue(
            np.isnan(df.at[0, 'responsible']),
            'No one should be responsible for finanzgeschaefte yet.')

        self.assertFalse(
            df.at[0, 'is_done'],
            'The link should have a default False when newly initiated.')

        self.assertFalse(
            len(df[df['Destination'].str.contains('brettterpstra')]),
            'The link containing brettterpstra is not in the new report.')

        self.assertTrue(
            len(df[df['Destination'].str.contains('gruener')]),
            'The link containing gruener is in the new report.')

    def test_merging_data(self):
        create_file_listing_block_with_report(self.portal)
        dashboard = Dashboard(self.portal, self.request)
        # set annotations to update later
        dashboard.dashboard_model._set_annotation(ANNOTATION_ASSET)

        # load dashboard again
        dashboard = Dashboard(self.portal, self.request)
        df = dashboard.dashboard_model.data

        self.assertEqual(
            'hugo', df.at[0, 'responsible'],
            'The user \'hugo\' should be responsible for finanzgeschaefte.')

        self.assertFalse(
            df.at[0, 'is_done'],
            'The link was marked done but appeared in new report again.')

        self.assertFalse(
            len(df[df['Destination'].str.contains('brettterpstra')]),
            'The link containing brettterpstra is not in the new report.')

        self.assertTrue(
            len(df[df['Destination'].str.contains('gruener')]),
            'The link containing gruener is in the new report.')
