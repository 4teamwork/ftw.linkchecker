from Products.CMFPlone.utils import safe_unicode
from ftw.linkchecker import LOGGER_NAME
from ftw.linkchecker import report_mailer
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.link import Link
from io import BytesIO
from plone import api
import logging
import plone
import re
import time
import transaction
import xlsxwriter


LABELS = Link()
LABELS.is_internal = 'Internal/External'
LABELS.link_origin = 'Origin'
LABELS.link_target = 'Destination'
LABELS.status_code = 'Status Code'
LABELS.content_type = 'Content Type'
LABELS.response_time = 'Response Time'
LABELS.error_message = 'Error Message'
LABELS.creator = 'Creator'
LABELS.source_state = 'Review State'
LABELS = [LABELS]


class ReportCreator(object):

    def __init__(self):
        self.row = 0
        self.output_xlsx = BytesIO()
        self.workbook = xlsxwriter.Workbook(self.output_xlsx,
                                            {'in_memory': True,
                                             'strings_to_url': False})
        self.worksheet = self.workbook.add_worksheet()
        self.table = []

    def append_report_data(self, link_objs, base_uri, format=None):
        format = format.get_workbook_format(self.workbook) if format else None
        for link_obj in link_objs:

            int_ext_link = link_obj.is_internal
            if link_obj.is_internal is None:
                int_ext_link = 'Unknown'
            elif link_obj.is_internal is True:
                int_ext_link = 'Internal Link'
                link_obj.status_code = 404
            elif link_obj.is_internal is False:
                int_ext_link = 'External Link'

            # remove portal path in link_target and link_origin
            portal_path_segments = api.portal.get().getPhysicalPath()
            portal_reg = re.compile('^' + '/'.join(portal_path_segments))
            link_obj.link_origin = re.sub(portal_reg, safe_unicode(base_uri),
                                          safe_unicode(link_obj.link_origin))
            link_obj.link_target = re.sub(portal_reg, safe_unicode(base_uri),
                                          safe_unicode(link_obj.link_target))

            self.worksheet.write(self.row, 0, int_ext_link, format)
            self.worksheet.write_string(self.row, 1,
                                        safe_unicode(link_obj.link_origin),
                                        format)
            self.worksheet.write_string(self.row, 2,
                                        safe_unicode(link_obj.link_target),
                                        format)
            self.worksheet.write(self.row, 3,
                                 safe_unicode(link_obj.status_code), format)
            self.worksheet.write(self.row, 4,
                                 safe_unicode(link_obj.content_type), format)
            self.worksheet.write(self.row, 5,
                                 safe_unicode(link_obj.response_time), format)
            self.worksheet.write(self.row, 6,
                                 safe_unicode(link_obj.error_message), format)
            self.worksheet.write(self.row, 7,
                                 safe_unicode(link_obj.creator), format)
            self.worksheet.write(self.row, 8,
                                 safe_unicode(link_obj.source_state), format)

            self.row += 1
        self.table.extend(link_objs)

    def add_general_autofilter(self):
        self.worksheet.autofilter(0, 0, self.row,
                                  len(LABELS[0].table_attrs) - 1)

    def get_column_widths(self):
        columns_size = [0] * len(self.table[0].table_attrs)
        for row in self.table:
            for j, column_element in enumerate(row):
                columns_size[j] = max(columns_size[j], len(column_element))
                # enlarge column width by content up to 100 characters
                if columns_size[j] > 100:
                    columns_size[j] = 100
        return columns_size

    def cell_width_autofitter(self):
        column_widths = self.get_column_widths()
        for row, column_width in enumerate(column_widths):
            self.worksheet.set_column(self.row, row, column_width + 7)

    def safe_workbook(self):
        self.workbook.close()

    def get_workbook(self):
        self.output_xlsx.seek(0)
        return self.output_xlsx


class ReportHandler(object):

    def __init__(self, site, accumulator):
        self._site = site
        self._accumulator = accumulator

        self._xlsx_file = self._create_excel_report(
            (self._accumulator.internal_broken_link_objs +
                self._accumulator.external_broken_link_objs),
            self._site.configuration.base_uri)
        self._xlsx_file_content = self._xlsx_file.read()
        self._file_name = self._generate_file_name()

    def send_report(self):
        self._send_mail_with_excel_report_attached(
            self._site.configuration.email,
            self._site.obj,
            self._accumulator.time_external_routine,
            self._xlsx_file_content,
            self._file_name)

    def upload_report(self):
        if self._site.upload_path:
            self._upload_report_to_filelistingblock(
                self._site.upload_path,
                self._xlsx_file,
                self._file_name)

    def _generate_file_name(self):
        return u'linkchecker_report_{}.xlsx'.format(
            time.strftime('%Y_%b_%d_%H%M%S', time.gmtime()))

    def _create_excel_report(self, link_objs, base_uri):
        file_i = ReportCreator()
        file_i.append_report_data(LABELS,
                                  base_uri,
                                  BOLD &
                                  CENTER &
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)
        file_i.append_report_data(link_objs, base_uri,
                                  DEFAULT_FONTNAME &
                                  DEFAULT_FONTSIZE)

        file_i.add_general_autofilter()
        file_i.cell_width_autofitter()
        file_i.safe_workbook()
        xlsx_file = file_i.get_workbook()
        return xlsx_file

    def _send_mail_with_excel_report_attached(
            self, email_addresses, plone_site_obj,
            total_time_fetching_external, xlsx_file_content, file_name):

        email_subject = 'Linkchecker Report'
        email_message = '''
        Dear Site Administrator, \n\n
        Please check out the linkchecker report attached to this mail.\n\n
        It took {}ms to fetch the external links for this report.\n\n
        Friendly regards,\n
        your 4teamwork linkcheck reporter\n\n\n
        '''.format(total_time_fetching_external)
        plone_site_path = '/'.join(plone_site_obj.getPhysicalPath())
        portal = api.content.get(plone_site_path)
        report_mailer_instance = report_mailer.MailSender(portal)

        for email_address in email_addresses:
            report_mailer_instance.send_feedback(
                email_subject, email_message, email_address,
                xlsx_file_content, file_name)

    def _upload_report_to_filelistingblock(
            self, filelistingblock_url, xlsx_file, file_name):
        portal = api.portal.get()
        try:
            file_listing_block = portal.unrestrictedTraverse(
                path=filelistingblock_url.encode('utf-8'))
        except KeyError:
            logger = logging.getLogger(LOGGER_NAME)
            logger.exception(
                'Error while uploading report: upload location is not a valid path: {}'.format(
                    filelistingblock_url.encode('utf-8')))
        else:
            xlsx_file.seek(0)
            data = xlsx_file.read()

            file_ = plone.api.content.create(
                container=file_listing_block, type='File',
                title=file_name, file=data)
            file_.setFilename(file_name)
            transaction.commit()
