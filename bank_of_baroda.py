import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False

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

    Bank_Name = "Baroda Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)


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
        df.drop(drop_column, axis=1, inplace=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
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

    Bank_Name = "Baroda Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", row_tol=12)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        drop_row = []
        for index, row in df.iterrows():
            date_match = re.search(date_pattern, row[0])
            if "DATE" not in row[0] and (not date_match or "Page" in row[2]):
                drop_row.append(index)
        if len(df.columns) == 5:
            df.insert(2, "chq info", "")
        df = df.drop(drop_row).reset_index(drop=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True

# Done
# 27_BHUMI BOB 01.03.2023 TO 31.03.2023.pdf
# pattern: "Serial/\nNoTransaction/\nDateValue/\nDateDescription Cheque/\nNumberDebit Credit Balance"
def Pattern20(pdf_file, csv_output):
    pattern_text = "Serial\nNoTransaction\nDateValue\nDateDescription Cheque\nNumberDebit Credit Balance\n"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern20")

    Bank_Name = "Baroda Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)
    # print(csv_output)
    skip_first = True
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", row_tol=14)
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    # For avoiding duplicate
    isInserted = []
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("csv_output.csv" ,mode='a',index=False,header=False)
        j = 0
        merged_row = []
        if i == 0:
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
        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 1])
            if date_match:
                if df.loc[j, 0] in isInserted:
                    j += 1
                    continue
                isInserted.append(df.loc[j, 0])
                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
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
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return
    # print("Pattern21")

    Bank_Name = "Baroda Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)

    date_pattern = r"\d{2}/\d{2}/\d{4}"
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
            if date_match:
                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)

    global Success
    Success = True
    return