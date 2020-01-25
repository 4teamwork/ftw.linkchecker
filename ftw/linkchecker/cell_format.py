class CellFormat(object):

    def __init__(self, format):
        self.format = format

    def __and__(self, cls):
        format = self.format
        format.update(cls.format)
        return CellFormat(format)

    def get_workbook_format(self, workbook):
        return workbook.add_format(self.format)


BLUE = CellFormat({'color': 'blue'})
BOLD = CellFormat({'bold': True})
CENTER = CellFormat({'align': 'center'})
DATE_FORMAT = CellFormat({'num_format': 'mmmm d yyyy'})
DEFAULT_FONTNAME = CellFormat({'font_name': 'Courier New'})
DEFAULT_FONTSIZE = CellFormat({'font_size': 10})
ITALIC = CellFormat({'italic': True})
RED = CellFormat({'color': 'red'})
