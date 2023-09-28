import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern4,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 10_SBI_2. 1.6.2021 to 20.7.2021 OK.pdf
# 10_1_1. SBI.pdf
# pattern: "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
# pattern: "Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
def Pattern4(pdf_file, csv_output):
    pattern_text1 = "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
    pattern_text2 = (
        "Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
    )
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text1
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    # print("Pattern4")
    global Success

    if extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", joint_tol=20)
        df_total = pd.DataFrame()
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            # camelot.plot(tables[i], kind='grid')
            # plt.show(block=True)
            df = df.drop(0)
            if i == 0:
                df.loc[-1] = [
                    "Txn Date",
                    "Value Date",
                    "Description",
                    "Ref No./Cheque",
                    "No.Branch Code",
                    "Debit",
                    "Credit",
                    "Balance",
                ]  # adding a row
                df.index = df.index + 1  # shifting index
                df.sort_index(inplace=True)
            df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
        if  extracting_utility.get_duplicate_remove():
            df = df_total.drop_duplicates().reset_index(drop=True)
        df.to_csv(csv_output, mode="a", index=False, header=False)
        Success = True
    # 10_1_1. SBI.pdf
    if extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
        df_total = pd.DataFrame()
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            if i != 0:
                df = df.drop(0)

            # # print("Pattern4222")
            for index, row in df.iterrows():
                match = re.search(r"\s\d{4}", row[1])
                if match:
                    year = match.group(0)
                    updated_string = row[1][: match.start()] + year
                    remainder = row[1][match.end() :]
                    # print(f"index:: {index}")
                    # print("_____")
                    # print(match.start())
                    # print(match.end())
                    # print("_____")
                    # print(row[1])
                    # print(row[2])
                    # print("_____")
                    # print(updated_string)
                    # print("_____")
                    # print(remainder)
                    row[1] = updated_string
                    row[2] = remainder + row[2]
                    # print("_____")
                    # print(row[1])
                    # print(row[2])
                elif row[1] == "":
                    match = re.search(r"\s\d{4}", row[2])
                    year = match.group(0)
                    updated_string = row[2][: match.end()]
                    remainder = row[2][match.end() :]
                    row[1] = updated_string
                    row[2] = remainder
            df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
        if  extracting_utility.get_duplicate_remove():
            df = df_total.drop_duplicates().reset_index(drop=True)
        df.to_csv(csv_output, mode="a", index=False, header=False)
        Success = True
    return
