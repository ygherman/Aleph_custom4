import sys

from helper_fuctions import *

level_mapper = {
    'אוסף': 'Section Record',
    'חטיבה': 'Fonds Record',
    'תת-חטיבה': 'Sub-Fonds Record',
    'תת חטיבה': 'Sub-Fonds Record',
    'סדרה': 'Series Record',
    'תת-סדרה': 'Sub-Series Record',
    'תת סדרה': 'Sub-Series Record',
    'תיק': 'File Record',
    'פריט': 'Item Record',
    'סידרה': 'Series Record',
    'תת-סידרה': 'Sub-Series Record'
}


def main():
    collection, client, file_id = fetch_gspread_id(input('type collection id:'))
    df = create_xl_from_gspread(client, file_id)
    create_import_table(df, collection)
    input_file_path, collection = open_id_list()
    xl = pd.ExcelFile(input_file_path)

    df = xl.parse('Sheet1')
    df.replace({'רמת תיאור': level_mapper}, inplace=True)
    df = fill_table(df, collection)
    out_path_excel = Path.cwd() / 'output_files' / (collection + '_brief_' + dt_now + '.xlsx')
    write_excel(df, out_path_excel)
    count, run_time = create_brief_MARC_XML(df, collection)
    sys.stderr.write("%s total records written to file in %s seconds.\n\n" % \
                     (count, run_time))


if __name__ == "__main__":
    main()
