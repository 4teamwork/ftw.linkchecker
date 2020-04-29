from plone import api
from zope.annotation.interfaces import IAnnotations
from zope.publisher.browser import BrowserView
import io
import pandas as pd


class Dashboard(BrowserView):

    def __init__(self, context, request):
        super(Dashboard, self).__init__(context, request)
        self.dashboard_model = DashboardModel(self.context, self.request)
        self.graph_generator = GraphGenerator()


class DashboardModel(object):

    def __init__(self, context, request):
        self.request = request
        self.context = context

    def _get_report_path(self):
        return api.portal.get_registry_record(
            'ftw.linkchecker.dashboard_storage')

    def _set_annotation(self, data):
        annotations = IAnnotations(self.context)
        annotations['ftw.linkchecker.link_data'] = data

    def _get_annotation(self):
        annotations = IAnnotations(self.context)
        return annotations['ftw.linkchecker.link_data']

    def _get_latest_report_from_excel(self):
        portal = api.portal.get()
        report_path = self._get_report_path().encode('utf-8')
        file_listing_block = portal.unrestrictedTraverse(report_path)
        reports = file_listing_block.items()

        # TODO sort reports by date newest to oldest

        filename, report = reports[0]
        return pd.read_excel(io.BytesIO(report.get_data()))


class GraphGenerator(object):
    pass
