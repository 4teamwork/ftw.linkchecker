from datetime import datetime
from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.publisher.browser import BrowserView
import io
import pandas as pd
import time


class Dashboard(BrowserView):

    def __init__(self, context, request):
        super(Dashboard, self).__init__(context, request)
        self.dashboard_model = DashboardModel(self.context, self.request)
        self.graph_generator = GraphGenerator()


class DashboardModel(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context

        self.data = None
        self._persisted_data = self._get_annotation()
        self._timestamp_old = self._persisted_data.get('timestamp', 0)
        self._timestamp_new = None
        self._reports = self._load_and_sort_fileblock_reports()

        self._latest_report_df = self._get_latest_report_df_from_excel()
        if isinstance(self._latest_report_df, pd.DataFrame):
            # there is new data
            if self._persisted_data:
                # update existing data
                self.data = self._update_data()
            else:
                # add data the first time
                pass
        else:
            # no data or no new data found
            self.data = self._persisted_data

    def _update_data(self):
        # use only key cols and unique cols
        df_old = pd.DataFrame.from_dict(self._persisted_data['report_data'])
        df_old = df_old[['Origin', 'Destination', 'responsible']]
        # use all cols plus add is_done with default False
        df_new = self._latest_report_df
        df_new['is_done'] = False
        # merge by keys Origin and Destination
        merged = df_old.merge(df_new, on=['Origin', 'Destination'], how='outer')
        # if Internal/External is NaN (only in old report) -> drop row
        merged = merged[merged['Internal/External'].notna()]

        self._set_annotation(
            {'timestamp': self._timestamp_new,
             'report_data': merged.to_dict('records')})

        return merged

    def _get_report_path(self):
        return api.portal.get_registry_record(
            'ftw.linkchecker.dashboard_storage')

    def _set_annotation(self, data):
        annotations = IAnnotations(self.context)
        annotations['ftw.linkchecker.link_data'] = data

    def _get_annotation(self):
        annotations = IAnnotations(self.context)
        try:
            return annotations['ftw.linkchecker.link_data']
        except KeyError:
            return {}

    def _has_more_recent_report(self):
        if not self._reports:
            return

        dt_current = datetime.fromtimestamp(self._timestamp_old)
        if self._reports[0][0] > dt_current:
            return True

    def _load_and_sort_fileblock_reports(self):
        portal = api.portal.get()
        report_path = self._get_report_path().encode('utf-8')
        try:
            file_listing_block = portal.unrestrictedTraverse(report_path)
        except KeyError:
            return
        reports = file_listing_block.items()
        if not reports:
            return
        # sort by date in file name (latest first)
        reports = [
            (datetime.strptime(report[0][19:-5], '%Y_%b_%d_%H%M%S'), report[1])
            for report in reports]
        reports.sort(key=lambda x: x[0], reverse=True)

        return reports

    def _get_latest_report_df_from_excel(self):
        if not self._reports or not self._has_more_recent_report():
            return
        report_date, report = self._reports[0]
        self._timestamp_new = int(time.mktime(report_date.timetuple()))
        return pd.read_excel(io.BytesIO(report.get_data()))


class GraphGenerator(object):
    pass
