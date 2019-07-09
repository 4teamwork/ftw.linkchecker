from Products.CMFPlone.utils import safe_unicode
from ftw.linkchecker.command import broken_link
from io import BytesIO
from plone import api
import re
import xlsxwriter

LABELS = broken_link.BrokenLink()
LABELS.is_internal = 'Internal/External'
LABELS.link_origin = 'Origin'
LABELS.link_target = 'Destination'
LABELS.status_code = 'Status Code'
LABELS.content_type = 'Content Type'
LABELS.response_time = 'Response Time'
LABELS.error_message = 'Error Message'
LABELS.creator = 'Creator'
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
