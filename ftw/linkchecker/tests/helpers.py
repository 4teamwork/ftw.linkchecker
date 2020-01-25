from Products.CMFDiffTool.utils import safe_utf8
from ftw.linkchecker import broken_link
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.configuration import Configuration
from ftw.linkchecker.report_generating import LABELS
from ftw.linkchecker.report_generating import ReportCreator
import os
import tempfile


CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))


def generate_test_data_excel_workbook():
    example_data = broken_link.BrokenLink()
    example_data.is_internal = 'Some'
    example_data.link_origin = 'example'
    example_data.link_target = 'data'
    example_data.status_code = 'to'
    example_data.content_type = 'fill'
    example_data.response_time = 'the'
    example_data.error_message = 'sheet'
    example_data.creator = 'slowly'
    example_data.source_state = 'man!'
    exemplar_report_data = [example_data] * 9

    base_uri = 'http://www.example_uri.com'
    file_i = ReportCreator()
    file_i.append_report_data(LABELS,
                              base_uri,
                              BOLD &
                              CENTER &
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)
    file_i.append_report_data(exemplar_report_data,
                              base_uri,
                              DEFAULT_FONTNAME &
                              DEFAULT_FONTSIZE)
    file_i.add_general_autofilter()
    file_i.cell_width_autofitter()
    file_i.safe_workbook()
    xlsx_file = file_i.get_workbook()

    return xlsx_file


class ConfigurationMock(Configuration):
    def _parse_arguments(self, args):
        config_path = os.path.join(
            CURRENT_PATH,
            'exemplar_data/exemplar_config.json')

        log_dir = tempfile.mkdtemp()
        log_path = os.path.join(log_dir, 'linkchecker.log')
        open(log_path, 'a').close()

        self.config_file_path = safe_utf8(config_path)
        self.log_file_path = safe_utf8(log_path)
