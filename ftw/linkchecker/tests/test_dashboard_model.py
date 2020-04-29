from ftw.builder import Builder
from ftw.builder import create
from ftw.linkchecker.browser.dashboard import Dashboard
from ftw.linkchecker.tests import FunctionalTestCase
from ftw.linkchecker.tests.exemplar_data.annotation_asset import ANNOTATION_ASSET
from plone import api
import os
import pandas as pd
import transaction


ASSET_NAME = 'linkchecker_report_2020_Feb_28_130820.xlsx'
TEST_FOLDER_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_REPORT = os.path.join(TEST_FOLDER_PATH, 'exemplar_data', ASSET_NAME)


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

    def test_read_data_from_excel_report(self):
        self.create_file_listing_block_with_report()
        dashboard = Dashboard(self.portal, self.request)

        # prepare dataframes to compare
        df_expected = pd.read_excel(TEST_REPORT)
        df_actual = dashboard.dashboard_model._latest_report_df

        pd.testing.assert_frame_equal(df_expected, df_actual)

    def test_first_time_loading_page_with_no_persisted_data(self):
        # TODO: implement
        pass

    def test_merging_data(self):
        self.create_file_listing_block_with_report()
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

    def create_file_listing_block_with_report(self):
        # build structure so that there is an excel report at
        # linkchecker/reports which is the default in registry.xml
        linkchecker_page = create(Builder('sl content page')
                                  .titled(u'linkchecker')
                                  .within(self.portal))
        file_listing_block = create(Builder('sl listingblock')
                                    .titled(u'reports')
                                    .within(linkchecker_page))

        # upload test asset to the file listing block
        with open(TEST_REPORT, 'rb') as f_:
            f_.seek(0)
            data = f_.read()
        file_ = api.content.create(
            container=file_listing_block, type='File',
            title=ASSET_NAME, file=data)
        file_.setFilename(ASSET_NAME)
        transaction.commit()
