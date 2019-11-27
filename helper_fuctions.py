import datetime
# script timer
import time
from pathlib import Path

import pandas as pd
from pymarc import Record, Field, XMLWriter

start_time = time.time()

dt_now = datetime.datetime.now().strftime('%Y%m%d')


def open_id_list():
    while True:
        file_name = input('please enter the name of the file that contains the list of identifiers:')
        file_path = Path.cwd() / 'input_files' / (file_name)
        if Path.exists(file_path):
            collection = input('please enter the name of the collection:')
            if len(collection) > 0:
                break
            else:
                print("you did not enter a name")
        else:
            print("you did not enter a file name")

    return file_path, collection


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
    if row['351'] in ['פריט', 'תיק']:
        return '00000npd#a22######a#4500'
    else:
        return '00000npc#a22######a#4500'


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
    df['Parent'] = ''
    df.loc[df.index[1:], 'Parent'] = df.loc[df.index[1:], 'Parent'].apply(rootid_finder)
    df = df.reset_index()

    df['כותרת'] = df['כותרת'].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["", ""])

    df = df.rename(columns={'רמת תיאור': '351', 'סימול/מספר מזהה': '911', 'סימול': '911',
                            'כותרת': '24510', 'סימול פרויקט': '911'})

    # Create different LDR depending on level of description
    # 00000npd^a22^^^^^^a^4500  - for file and item level records
    # 00000npc^a22^^^^^^^^4500 - for all other levels (the "c" is for "collection")
    df['LDR'] = None
    df['LDR'] = df.apply(create_LDR, axis=1)
    df['008'] = '^k^^^^^^^^xx^^^^^^^^^^^^^^^^^^^^^^d'
    df['911'] = df['911'].apply(lambda x: '$$a' + x + '$$c' + collect)
    df['041'] = '$$aheb'
    df['351'] = df['351'].apply(lambda x: '$$c' + x)
    df['24510'] = df['24510'].apply(lambda x: '$$a' + x)
    df['906'] = '$$aVIS'
    df['999_1'] = '$$aARCHIVE'
    df['999_2'] = '$$bNOULI'
    df['999_3'] = '$$bNOOCLC'
    df['FMT'] = 'MX'
    df['948'] = '$$aNNL'
    df['5420'] = '$$lCopyright status not determined; ' + \
                 'Contract$$nNo copyright analysis' + \
                 '$$oNoam Solan by Yael Gherman {}$$qללא ניתוח מצב זכויות'.format(dt_now)
    df['5061'] = '$$aLibrary premises only;$$bPermissions officer;$$eIsrael Copyright Act$$0000000008'
    df['540'] = '$$aאיסור העתקה' + \
                '$$uhttp://web.nli.org.il/sites/NLI/Hebrew/library/items-terms-of-use/Pages/nli-copying-prohibited.aspx'

    ordered_col = ['911', '351', 'LDR', '008', '24510', '906', '041',
                   '999_1', '999_2', '999_3', 'FMT', '948', '5420', '5061', '540']

    df = df[ordered_col]
    # df = df.rename(columns={'999': '999##b'})

    return df


def create_brief_MARC_XML(df, collectionID):
    """

    :param df:
    :return:
    """
    output_file = Path.cwd() / 'output_files' / (collectionID + '_brief_' + dt_now + ".xml")
    writer = XMLWriter(open(output_file, 'wb'))

    # counter for records
    count = 1

    for index, row in df.iterrows():
        # create  a marc record instance
        record = Record()

        for col in df:
            # if field is empty, skip
            if str(row[col]) == '':
                continue
            # leader
            elif col == 'LDR':
                l = list(record.leader)
                l[0:5] = '0000'
                l[5] = 'n'
                l[6] = 'p'
                if row['351'] == 'File Record' or 'Item Record':
                    l[7] = 'c'
                else:
                    l[7] = 'd'
                l[9] = 'a'  # flag saying this record is utf8
                record.leader = "".join(l)

                continue
            # 008
            elif col == '008':
                field = Field(tag='008', data=row[col])
            else:

                # extract field name
                field = col[:3]

                # extract indicators
                if col.find('_') == -1 and len(col) < 5:
                    ind = [' ', ' ']
                elif col.find('_') == 3:
                    ind = [' ', ' ']
                elif col.find('_') == 4:
                    ind = [col[3], ' ']
                elif col.find('_') == 5:
                    ind = [' ', col[4]]
                else:
                    ind = [col[3], col[4]]

                subfields_data = list()
                subfields_prep = list(filter(None, row[col].split('$$')))
                for subfield in subfields_prep:
                    if subfield == '':
                        continue
                    subfields_data.append(subfield[0])
                    subfields_data.append(subfield[1:])
                # record.add_field(
                #     Field(
                #         tag=field,
                #         indicators=ind,
                #         subfields=subfields_data))

                print('field:', field)
                print('subfields:', subfields_data)

                record.add_field(
                    Field(
                        tag=field,
                        indicators=ind,
                        subfields=subfields_data))

        writer.write(record)
        # sys.stderr.write("Record: %s\n%s\n" % (count, str(record)))
        # counter
        count += 1
    writer.close()
    run_time = time.time() - start_time
    return count, run_time
