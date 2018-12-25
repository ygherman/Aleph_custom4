import os

import pandas as pd

field_mapper = {
    'collection': '911##c',
    'סימול/מספר מזהה': '911##a'
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


def fill_table(df, collect):
    """

    :type collect: object
    """

    lambda x: True if x % 2 == 0 else False

    df = df.set_index('סימול/מספר מזהה')
    rootid_finder = lambda x: x[:find_nth(x, '-', x.count('-'))]
    df['Parent'] = df.index
    df.loc[df.index[1:], 'Parent'] = df.loc[df.index[1:], 'Parent'].apply(rootid_finder)
    df = df.reset_index()

    df = df.rename(columns={'רמת תיאור': '351##c', 'סימול/מספר מזהה': '911##a'})

    # Create different LDR depending on level of description
    # 00000npd^a22^^^^^^a^4500  - for file and item level records
    # 00000npc^a22^^^^^^^^4500 - for all other levels (the "c" is for "collection")
    df['LDR'] = None

    def create_LDR(row):
        if row['351##c'] in ['פריט', 'תיק']:
            return '00000npd^a22^^^^^^a^4500'
        else:
            return '00000npc^a22^^^^^^^^4500'

    df['LDR'] = df.apply(create_LDR, axis=1)

    df = df.set_index('911##a')

    df['008'] = '^^^^^^k^^^^^^^^xx^^^^^^^^^^^^^^^^^^^^^^d'
    df['911##c '] = collect
    df['24500a'] = 'Add Title'
    df['BAS##a'] = 'VIS'
    df['999'] = '$$aARCHIVE$$bNOULI$$bNOOCLC'
    df['FMT'] = 'MX'
    df['OWN##a'] = 'NNL'

    return df


file_name, collection = open_id_list()
xl = pd.ExcelFile(file_name)
df = xl.parse('Sheet1')
df = fill_table(df, collection)
write_excel(df, os.path.join(os.getcwd(), file_name.replace('.xlsx', '_custom04.xlsx')), collection + '_custom04')
