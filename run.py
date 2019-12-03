from helper_fuctions import *

dt_now = datetime.datetime.now().strftime('%Y%m%d')

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
    input_file_path, collection = open_id_list()
    xl = pd.ExcelFile(input_file_path)

    df = xl.parse('Sheet1')
    df.replace({'רמת תיאור': level_mapper}, inplace=True)
    df = fill_table(df, collection)

    out_path_excel = Path.cwd() / 'output_files' / (collection + 'custom04' + dt_now + '.xlsx')
    write_excel(df, out_path_excel, collection + '_custom04')

    out_path_txt = Path.cwd() / 'output_files' / (collection + 'custom04' + dt_now + '.txt')
    df.to_csv(out_path_txt, sep='\t', encoding='utf8')


if __name__ == "__main__":
    main()
