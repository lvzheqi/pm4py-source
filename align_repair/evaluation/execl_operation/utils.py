import xlrd
import xlwt


def open_excel(file):
    try:
        data = xlrd.open_workbook(file)
        return data
    except Exception as e:
        print(e)


def create_workbook():
    return xlwt.Workbook(encoding='utf-8')


def read_table_columns(file, sheet_index, columns):
    data = open_excel(file)
    table = data.sheets()[sheet_index]
    content = list()
    for row_num in range(table.nrows):
        row = table.row_values(row_num)
        content.append([row[col] for col in columns]) if row else None
    return content


def read_table_rows(file, sheet_index, rows):
    data = open_excel(file)
    table = data.sheets()[sheet_index]
    return [table.row_values(row_num) for row_num in rows]


def write_row_to_table(table, row, info):
    for i in range(len(info)):
        table.write(row, i, info[i])


def write_column_to_table(table, col, info):
    for i in range(len(info)):
        table.write(i, col, info[i])


def save(base, name):
    base.save(name)
