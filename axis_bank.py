import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False

def initialize(pdf_file, csv_output):
    patterns = [
            Pattern2,
        ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break

# Done
# 2_axis_1. 01-04-2021 to 13-10-2021.pdf
# 2b_2. AXIS BANK.pdf
# pattern: "Tran Date Chq No Particulars Debit Credit Balance Init."


def Pattern2(pdf_file, csv_output):
    pattern_text = "Tran Date Chq No Particulars Debit Credit Balance Init"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Axis Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)
    # print("Pattern2")
    column_name_appened = False
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", line_scale=40)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        for index, row in df.iterrows():
            match = re.search(r"[a-zA-Z]", row[1])
            if match:
                year = match.group(0)
                updated_string = row[1][: match.start()]
                remainder = row[1][match.start() :]
                row[1] = updated_string
                row[2] = remainder + row[2]
        if column_name_appened is False:
            column_name_appened = True
            df = df.drop(0)
            df.loc[-1] = [
                "Tran Date",
                "Chq No",
                "Particulars",
                "Debit",
                "Credit",
                "Balance",
                "Init. br",
            ]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    # tables[i].to_csv(csv_output ,mode='a')
    global Success
    Success = True
    return