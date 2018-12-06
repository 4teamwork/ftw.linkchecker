class CellFormat(object):

    def __init__(self, format):
        self.format = format

    def __and__(self, cls):
        format = self.format
        format.update(cls.format)
        return CellFormat(format)

    def get_workbook_format(self, workbook):
        return workbook.add_format(self.format)


BOLD = CellFormat({'bold': True})
DATE_FORMAT = CellFormat({'num_format': 'mmmm d yyyy'})
ITALIC = CellFormat({'italic': True})
RED = CellFormat({'color': 'red'})
BLUE = CellFormat({'color': 'blue'})
CENTER = CellFormat({'align': 'center'})
DEFAULT_FONTNAME = CellFormat({'font_name': 'Courier New'})
DEFAULT_FONTSIZE = CellFormat({'font_size': 10})
