import click
import xml.etree.ElementTree as ET

from mxl2xlsx import score, write


@click.command()
@click.argument('mxl_file_path', required=True, type=click.Path(
    exists=True, file_okay=True, readable=True, resolve_path=True))
@click.argument('excel_out_file_path', type=click.Path(
    exists=False), default='partitur.xlsx')
def main(mxl_file_path, excel_out_file_path):
    """
    This program accepts a music XML file (specified in MXL_FILE_PATH)
    and returns a Microsoft Excel formatted partitur, which can be
    specified or defaults to "partitur.xlsx".
    """
    mxml = ET.parse(mxl_file_path)
    title = mxml.getroot().find('work/work-title')
    if title is not None:
        score_title = title.text
    else:
        score_title = ''

    excel_grid = score.parse_mxl(mxml)

    write.write_to_excel(excel_out_file_path, excel_grid, score_title)


if __name__ == '__main__':
    main()
