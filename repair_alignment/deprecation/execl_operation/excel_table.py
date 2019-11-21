class ExcelTable(object):
    def __init__(self, table):
        self._row = 0
        self._column = 0
        self._table = table

    def _get_row(self):
        self._row += 1
        return self._row - 1

    def _get_column(self):
        self._column += 1
        return self._column - 1

    def _get_table(self):
        return self._table

    row = property(_get_row)
    column = property(_get_column)
    table = property(_get_table)
