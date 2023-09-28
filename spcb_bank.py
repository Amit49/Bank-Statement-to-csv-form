import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern16,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 24_SURAT PEOPLE CO-PO BANK 1.4.21 TO 30.9.2021.pdf
# pattern: "Date Particulars Withdr awals Deposits Balance"
def Pattern16(pdf_file, csv_output):
    pattern_text = "Date Particulars Withdr awals Deposits Balance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern16")

    Bank_Name = "SURAT PEOPLE CO-PO BANK (SPCB)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", row_tol=12)
    df = pd.DataFrame()

    for i in tqdm(range(tables.n)):
        df = pd.concat([df, tables[i].df], axis=0).reset_index(drop=True)
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
    j = 0
    merged_row = [["Date", "Particulars", "Withdrawal", "Deposit", "Balance"]]
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            if (
                j + 1 < (len(df))
                and df.loc[j + 1, 0] == ""
                and df.loc[j + 1, 1] != ""
            ):
                new_row = df.loc[j] + df.loc[j + 1]
                # print(f"New Row:::\n{new_row}")
                merged_row.append(new_row)
                j += 2
                continue
            else:
                merged_row.append(df.loc[j])
        j += 1
    df = pd.DataFrame(merged_row)
    if  extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates(subset=[0, 2, 3, 4], keep="last").reset_index(
            drop=True
        )
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
