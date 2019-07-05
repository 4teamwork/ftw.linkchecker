from ftw.linkchecker import report_generating
from ftw.linkchecker.cell_format import BOLD
from ftw.linkchecker.cell_format import CENTER
from ftw.linkchecker.cell_format import DEFAULT_FONTNAME
from ftw.linkchecker.cell_format import DEFAULT_FONTSIZE
from ftw.linkchecker.command import broken_link


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
    exemplar_report_data = [example_data] * 9

    base_uri = 'http://www.example_uri.com'
    file_i = report_generating.ReportCreator()
    file_i.append_report_data(report_generating.LABELS,
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
