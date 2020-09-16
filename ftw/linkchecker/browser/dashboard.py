from Products.CMFPlone.PloneBatch import Batch
from datetime import datetime
from plone import api
from plone.app.controlpanel.usergroups import UsersOverviewControlPanel
from zope.annotation.interfaces import IAnnotations
import base64
import io
import matplotlib
import numpy as np
import pandas as pd
import time

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa


class Dashboard(UsersOverviewControlPanel):

    def __call__(self):

        form = self.request.form
        submitted = form.get('form.submitted', False)
        search = form.get('form.button.Search', None) is not None
        findAll = form.get('form.button.FindAll', None) is not None
        self.searchString = not findAll and form.get('searchstring', '') or ''
        self.searchResults = []
        self.newSearch = False

        if search or findAll:
            self.newSearch = True

        if form.get('filter_submit'):
            apply_filter = form.get('filter')
            query = form.get('query')
            self.__init__(
                self.context, self.request,
                apply_filter={'filter': apply_filter, 'query': query})

        if form.get('target_state') and form.get('link_number'):
            target_state = form.get('target_state')
            link_number = form.get('link_number')
            self.dashboard_model.set_done_state(link_number, target_state)
            self.__init__(self.context, self.request)

        if submitted:
            assignment = [key for key in form.keys() if 'assign' in key]
            if assignment:
                link_number = assignment[0][-6:].split('_', 1)[0]
                userid = assignment[0][-6:].split('_', 1)[1]
                self.dashboard_model.assign_user(link_number, userid)
                self.__init__(self.context, self.request)

        # Only search for all ('') if the many_users flag is not set.
        if not(self.many_users) or bool(self.searchString):
            self.searchResults = self.doSearch(self.searchString)

        return self.index()

    def __init__(self, context, request, apply_filter=None):
        super(Dashboard, self).__init__(context, request)
        self.batch_size = 10
        self.dashboard_model = DashboardModel(
            self.context, self.request, apply_filter=apply_filter)
        self.graph_generator = GraphGenerator(
            self.dashboard_model.data, self.dashboard_model.history)

    @property
    def batch(self):
        b_start = self.request.form.get('b_start', 0)
        return Batch(self.get_links(), self.batch_size, b_start)

    def get_links(self):
        link_data = self.dashboard_model.data.to_dict('records')
        for link in link_data:
            for key in link:
                if key == 'Status Code' and not np.isnan(link[key]):
                    link[key] = int(link[key])
        return link_data


class DashboardModel(object):

    def __init__(self, context, request, apply_filter=None):
        self.request = request
        self.context = context

        self.data = None
        self._persisted_data = self._get_annotation()
        self._timestamp_old = self._persisted_data.get('timestamp', 0)
        self._timestamp_new = None
        self._reports = self._load_and_sort_fileblock_reports()
        self.history = self._collect_history()

        self._latest_report_df = self._get_latest_report_df_from_excel()
        if isinstance(self._latest_report_df, pd.DataFrame):
            # there is new data
            if self._persisted_data:
                # update existing data
                self.data = self._update_data()
            else:
                # add data the first time
                df_new = self._latest_report_df
                df_new['is_done'] = False
                df_new['id'] = df_new.index
                df_new['responsible'] = np.nan
                self._set_annotation(
                    {'timestamp': self._timestamp_new,
                     'report_data': df_new.to_dict('records')})
                self.data = df_new
        else:
            if self._persisted_data:
                # no new data found
                self.data = pd.DataFrame.from_dict(
                    self._persisted_data['report_data'])
            else:
                # no data found
                self.data = pd.DataFrame()

        if apply_filter:
            self._filter(apply_filter)

    def assign_user(self, link_id, user_id):
        report_data = self._persisted_data['report_data']

        updated_data = []
        for link in report_data:
            if str(link['id']) == link_id:
                link['responsible'] = user_id
            updated_data.append(link)

        self._set_annotation(
            {'timestamp': self._timestamp_old,
             'report_data': updated_data})

    def set_done_state(self, link_id, new_state):
        new_state = True if new_state == 'done' else False
        report_data = self._persisted_data['report_data']

        updated_data = []
        for link in report_data:
            if str(link['id']) == link_id:
                link['is_done'] = new_state
            updated_data.append(link)

        self._set_annotation(
            {'timestamp': self._timestamp_old,
             'report_data': updated_data})

    def _filter(self, apply_filter):
        query = apply_filter.get('query')
        filter_ = apply_filter.get('filter')

        if filter_ == 'by_user':
            current_user = api.user.get_current().getUserName()
            self.data = self.data.loc[self.data['responsible'] == current_user]
            return

        if filter_ == 'status' and query:
            try:
                query = float(query)
            except ValueError:
                return
            self.data = self.data.loc[self.data['Status Code'] == query]
            return

        if filter_ == 'by_done' and query:
            if query not in ['True', 'False', 'true', 'false', '1', '0']:
                return
            query = True if query in ['True', 'true', '1'] else False
            self.data = self.data.loc[self.data['is_done'] == query]
            return

        if filter_ == 'workflow_state' and query:
            self.data = self.data.loc[self.data['Review State'] == query]
            return

        if filter_ == 'internal_external' and query:
            self.data = self.data.loc[self.data['Internal/External'] == query]
            return

    def _collect_history(self):
        history_df = pd.DataFrame()
        if not self._reports:
            return history_df

        for report_date, report in self._reports:
            status_df = pd.read_excel(
                io.BytesIO(report.get_data()))[['Status Code']]
            cleaned_status_df = status_df[
                'Status Code'].fillna(0).astype(int).replace(0, 'NaN')
            quantity_per_status = cleaned_status_df.value_counts(
                    ).to_frame().T.rename({'Status Code': report_date})
            history_df = history_df.append(quantity_per_status)

        return history_df

    def _update_data(self):
        # use only key cols and unique cols
        df_old = pd.DataFrame.from_dict(self._persisted_data['report_data'])
        df_old = df_old[['Origin', 'Destination', 'responsible']]
        # use all cols plus add is_done with default False
        df_new = self._latest_report_df
        df_new['is_done'] = False
        df_new['id'] = df_new.index
        # merge by keys Origin and Destination
        merged = df_old.merge(df_new, on=['Origin', 'Destination'], how='outer')
        # if Internal/External is NaN (only in old report) -> drop row
        merged = merged.dropna(subset=['Internal/External'])

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

    def __init__(self, data_df, history_df):
        self.df = data_df
        self.history = history_df

    def get_status_plot(self):
        if not len(self.df):
            return
        status = self.df['Status Code'].fillna(0).astype(int).replace(0, 'NaN')
        quantity_per_status = status.value_counts(dropna=False)
        fig = plt.figure(figsize=(6, 6))
        fig = quantity_per_status.plot.pie(
            label='', title='By Status Codes').figure

        img_tag = self._generate_img_tag(fig)
        return img_tag

    def get_creator_plot(self):
        if not len(self.df):
            return
        creator = self.df['Creator']
        quantity_per_creator = creator.value_counts(dropna=False)
        fig = plt.figure(figsize=(6, 6))
        fig = quantity_per_creator.plot.pie(
            label='', title='By Creator').figure

        img_tag = self._generate_img_tag(fig)
        return img_tag

    def get_workflow_plot(self):
        if not len(self.df):
            return
        state = self.df['Review State']
        quantity_per_state = state.value_counts(dropna=False)

        # This assumes that workflows follow the pattern
        # <wf-name>--STATUS--<wf-state-name>
        index_replacement = {}
        new_labels = [{wf: wf.split('--')[-1]} for wf in quantity_per_state.index]
        [quantity_per_state.rename(index=new_label, inplace=True)
         for new_label in new_labels]

        fig = plt.figure(figsize=(6, 6))
        fig = quantity_per_state.plot.pie(
            label='', title='By Review State').figure

        img_tag = self._generate_img_tag(fig)
        return img_tag

    def get_history_plot(self):
        if not len(self.df):
            return
        fig = plt.figure()
        fig = self.history.plot(
            label='', title="History by Status Code", marker='D',
            figsize=(20, 6)).figure

        img_tag = self._generate_img_tag(fig)
        return img_tag

    def _generate_img_tag(self, fig):
        encoded = self._fig_to_base64(fig)
        return '<img src="data:image/png;base64, {}">'.format(
            encoded.decode('utf-8'))

    @staticmethod
    def _fig_to_base64(fig):
        img = io.BytesIO()
        fig.savefig(img, format='png',
                    bbox_inches='tight')
        img.seek(0)

        return base64.b64encode(img.getvalue())
