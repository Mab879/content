from utils.create_srg_export import setup_csv_writer
from utils.disa_utils import get_iacontrol


def handle_csv_output(output, results):
    with open(output, 'w') as csv_file:
        csv_writer = setup_csv_writer(csv_file)
        for row in results:
            csv_writer.writerow(row)


def handle_xlsx_output(output, product, results):
    output = output.replace('.csv', '.xlsx')
    for row in results:
        row['IA Control'] = get_iacontrol(row['SRGID'])
    convert_srg_export_to_xlsx.handle_dict(results, output, f'{product} SRG Mapping')
    return output


def handle_html_output(output, product, results):
    for row in results:
        row['IA Control'] = get_iacontrol(row['SRGID'])
    output = output.replace('.csv', '.html')
    convert_srg_export_to_html.handle_dict(results, output, f'{product} SRG Mapping')
    return output


def handle_output(output: str, results: list, format_type: str, product: str) -> None:
    if format_type == 'csv':
        handle_csv_output(output, results)
    elif format_type == 'xlsx':
        output = handle_xlsx_output(output, product, results)
    elif format_type == 'html':
        output = handle_html_output(output, product, results)

    print(f'Wrote output to {output}')
