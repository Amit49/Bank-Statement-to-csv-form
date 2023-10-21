import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern17,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 25_Union_Bank_1.8.2021 TO 31.3.2022.pdf
# pattern: "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
def Pattern17(pdf_file, csv_output):
    pattern_text = "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern17")

    Bank_Name = "Union Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [
                ["Tran Id", "Tran Date", "Remarks", "Amount (Rs.)", "Balance (Rs.)"]
            ]

        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 1])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                # print(f"Row:::\n{df.loc[j]}")
                if (
                    j + 1 < (len(df))
                    and df.loc[j + 1, 1] == ""
                    and df.loc[j + 1, 2] != ""
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
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if  extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
