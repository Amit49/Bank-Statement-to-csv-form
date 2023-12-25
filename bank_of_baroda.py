import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False
Bank_Name = "Baroda Bank"

def initialize(pdf_file, csv_output):
    patterns = [
        Pattern1,
        Pattern14,
        Pattern20,
        Pattern21,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 1_Baroda_1. 01.04.2021 TO 31.05.2021 OK.pdf
# pattern: S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate
def Pattern1(pdf_file, csv_output):
    pattern_text = "S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", row_tol=12)

    date_pattern = r"\d{2}-\d{2}-\d{4}"
    isInserted = []
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        drop_column = []
        df = tables[i].df
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [
                [
                    "S.No",
                    "Date",
                    "Description",
                    "Cheque No",
                    "Debit",
                    "Credit",
                    "Balance",
                    "Value Date",
                ]
            ]

        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 1])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                if df.loc[j, 0] in isInserted:
                    j += 1
                    continue
                isInserted.append(df.loc[j, 0])
                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        for column_index in range(4, len(df.columns)):
            for value in df.iloc[:, column_index]:
                if value == "":
                    if column_index is not drop_column:
                        drop_column.append(column_index)
                    break
        # dropping empty extra column
        if len(drop_column) > 0:
            df.drop(drop_column, axis=1, inplace=True)
            new_column_names = [0, 1, 2, 3, 4, 5, 6, 7]
            df = df.set_axis(new_column_names, axis=1)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total = df_total.iloc[:, :8]
    df_total.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 22_OpTransactionHistoryUX504-01-2023 (1).pdf
# pattern: "NARRATION DEPOSIT(CR) DATE CHQ.NO. WITHDRAWAL(DR) BALANCE(INR)"
def Pattern14(pdf_file, csv_output):
    pattern_text = "NARRATION DEPOSIT(CR) DATE CHQ.NO. WITHDRAWAL(DR) BALANCE(INR)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["76,360,457,571,695"]
    cols *= 128
    TR = ["0,1180,803,0"]
    TR *= 128

    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", row_tol=12, columns=cols, table_areas=TR
    )
    # tables.export('foo.csv', f='csv')

    df_total = pd.DataFrame()

    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
        # extracting_utility.show_plot_graph(tables[i])
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        drop_row = []
        for index, row in df.iterrows():
            date_match = re.search(date_pattern, row[0])
            if (
                "Statement of transactions in Savings Account" in row[0]
                or len(row[0]) > 12
            ):
                drop_row.append(index)
            if "DATE" not in row[0] and (not date_match or "Page" in row[2]):
                drop_row.append(index)
        if len(df.columns) == 5:
            df.insert(2, "chq info", "")
        df = df.drop(drop_row).reset_index(drop=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True


# Done
# 27_BHUMI BOB 01.03.2023 TO 31.03.2023.pdf
# pattern: "Serial/\nNoTransaction/\nDateValue/\nDateDescription Cheque/\nNumberDebit Credit Balance"
def Pattern20(pdf_file, csv_output):
    pattern_text = "Serial\nNoTransaction\nDateValue\nDateDescription Cheque\nNumberDebit Credit Balance\n"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    cols = ["42,97,145,320,362,435,495"]
    cols *= 128
    TA = ["0,720,580,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols, table_areas=TA,
        #row_tol 14 is improtant as date and description are not alligend
        row_tol=14,
    )
    # tables.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}-\d{2}-\d{4}"

    merged_row = [
                [
                    "Serial No",
                    "Transaction Date",
                    "Value Date",
                    "Description",
                    "Cheque Number",
                    "Debit",
                    "Credit",
                    "Balance",
                ]
            ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 1])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 1])
                if (
                    next_date_match
                    or df.loc[k, 1] != ""
                ):
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df = df.iloc[:, :8]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 1690969903.pdf
# pattern: "Transaction DetailsDateDescriptionAmountType"
# pattern: "Transaction Details\nDate Description Amount Type"
def Pattern21(pdf_file, csv_output):
    pattern_text1 = "Transaction DetailsDateDescriptionAmountType"
    pattern_text2 = "Transaction Details\nDate Description Amount Type"
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text1
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return
    # print("Pattern21")
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    date_pattern = r"\d{2}(/|-)\d{2}(/|-)\d{4}"
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [["Date", "Description", "Amount", "Type"]]

        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 0])
            if date_match and len(df.loc[j, 0]) < 12:
                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total = df_total.iloc[:, :4]
    df_total.to_csv(csv_output, mode="w", index=False, header=False)

    global Success
    Success = True
    return
