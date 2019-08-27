import os

import pandas as pd

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

def open_id_list():
    while True:
        file_name = input('please enter the name of the file that contains the list of identifiers:')
        file_name = str(file_name)
        if os.path.isfile(file_name):
            collection = input('please enter the name of the collection:')
            if len(collection) > 0:
                break
            else:
                print("you did not enter a name")
        else:
            print("you did not enter a file name")

    return file_name, collection


def find_nth(string, searchFor, n):
    """finds the n'th occurrence of a substring (searchFor) in a string.

    Returns:
        The position of the nth occurence of the substring in the given string.
    """
    start = string.find(searchFor)
    while start >= 0 and n > 1:
        start = string.find(searchFor, start + len(searchFor))
        n -= 1
    return start


def write_excel(df, path, sheets='Sheet1'):
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    """
    creates a excel file of a given dataframe
    :param df: the dateframe or a list of dataframes to write to excel
    :param path: the path name of the output file, or a list of sheets
    :param sheets: can be a list of sheet or
    :param
    """
    writer = pd.ExcelWriter(path, engine='xlsxwriter')

    # Convert the dataframe to an XlsxWriter Excel object.
    if type(df) is list and type(sheets) is list:
        i = 0
        for frame in df:
            frame.to_excel(writer, sheet_name=sheets[i])
            i += 1
    else:
        df.to_excel(writer, sheet_name=sheets)

    writer.close()


def create_LDR(row):
    if row['351##c'] in ['פריט', 'תיק']:
        return '00000npd^a22^^^^^^a^4500'
    else:
        return '00000npc^a22^^^^^^^^4500'

def fill_table(df, collect):
    """

    :param df: original DataFrame
    :type collect: object
    """

    if "סימול/מספר מזהה" in list(df.columns.values):
        df = df.set_index('סימול/מספר מזהה')
    elif "סימול" in list(df.columns.values):
        df = df.set_index('סימול')

    rootid_finder = lambda x: x[:find_nth(x, '-', x.count('-'))]
    df['Parent'] = df.index
    df.loc[df.index[1:], 'Parent'] = df.loc[df.index[1:], 'Parent'].apply(rootid_finder)
    df = df.reset_index()

    df = df.rename(columns={'רמת תיאור': '351##c', 'סימול/מספר מזהה': '911##a', 'סימול': '911##a',
                            'כותרת': '24510a'})

    # Create different LDR depending on level of description
    # 00000npd^a22^^^^^^a^4500  - for file and item level records
    # 00000npc^a22^^^^^^^^4500 - for all other levels (the "c" is for "collection")
    df['LDR'] = None

    df['LDR'] = df.apply(create_LDR, axis=1)

    df = df.set_index('911##a')

    df['008'] = '^^^^^^k^^^^^^^^xx^^^^^^^^^^^^^^^^^^^^^^d'
    df['911##c'] = collect
    df['BAS##a'] = 'VIS'
    df['999##a'] = 'ARCHIVE'
    df['999##b'] = 'NOULI'
    df['999##b_1'] = 'NOOCLC'
    df['FMT'] = 'MX'
    df['OWN##a'] = 'NNL'
    df['STA##a'] = 'SUPPRESSED'

    ordered_col = ['911##c', '351##c',
                   'LDR', '008', '24510a', 'BAS##a',
                   '999##a', '999##b', '999##b_1', 'FMT', 'OWN##a', 'STA##a']


    df = df[ordered_col]
    df = df.rename(columns={'999##b_1': '999##b'})


    return df


file_name, collection = open_id_list()
xl = pd.ExcelFile(file_name)

df = xl.parse('Sheet1')
df.replace({'רמת תיאור': level_mapper}, inplace=True)
df = fill_table(df, collection)
write_excel(df, os.path.join(os.getcwd(), file_name.replace('.xlsx',
                                                            '_custom04.xlsx').lower()), collection + '_custom04')
file_name = file_name.lower()
df.to_csv(os.path.join(os.getcwd(), file_name.replace('aleph.xlsx',
                                                      'custom04.txt')), sep='\t', encoding='utf8')
