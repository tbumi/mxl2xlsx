import xlsxwriter

COLUMN_WIDTH_IN_EXCEL = 4


def write_to_excel(file_path, excel_grid, title):
    workbook = xlsxwriter.Workbook(file_path)
    worksheet = workbook.add_worksheet()

    partitur_format = {
        'font_name': 'Partitur',
        'font_size': 12,
        'align': 'center'
    }
    normal_text_format = {
        'font_name': 'Calibri',
        'font_size': 11,
        'align': 'left',
        'bold': True
    }
    title_text_format = {
        'font_name': 'Cambria',
        'font_size': 20,
        'align': 'center',
        'bold': True
    }
    partitur_text = workbook.add_format(partitur_format)
    normal_text = workbook.add_format(normal_text_format)
    title_text = workbook.add_format(title_text_format)

    partitur_format_lborder = partitur_format.copy()
    partitur_format_lborder['left'] = 1
    partitur_text_lborder = workbook.add_format(partitur_format_lborder)

    partitur_format_rborder = partitur_format.copy()
    partitur_format_rborder['right'] = 1
    partitur_text_rborder = workbook.add_format(partitur_format_rborder)

    # write the title
    worksheet.merge_range(
        0, 0, 0, max(len(line) for line in excel_grid) - 1, title, title_text)

    for row_num, row_entries in enumerate(excel_grid):
        for col_num, col_entries in enumerate(row_entries):
            worksheet.set_column(col_num, col_num, COLUMN_WIDTH_IN_EXCEL)
            format_partitur_text = {
                'normal': normal_text,
                'partitur': partitur_text,
                'partitur_lborder': partitur_text_lborder,
                'partitur_rborder': partitur_text_rborder,
            }[col_entries['format']]
            worksheet.write(
                row_num, col_num, col_entries['text'], format_partitur_text)

    workbook.close()
