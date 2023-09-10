import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern15,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 23_paytm_1. 01.04.2021 TO 25.08.2021.pdf
# pattern: "DATE & TIME TRANSACTION DETAILS AMOUNT AVAILABLE BALANCE"
def Pattern15(pdf_file, csv_output):
    pattern_text = "DATE & TIME TRANSACTION DETAILS AMOUNT AVAILABLE BALANCE"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern15")

    Bank_Name = "Paytm Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all")
    date_pattern = r"\d{1} [A-Za-z]{3} \d{4}"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        j = 0
        merged_row = []
        if i == 0:
            # merged_row = [["Date","Narration","Chq/Ref No","Withdrawal (Dr)/Deposit (Cr)","Balance"]]
            merged_row = [
                ["DATE & TIME", "TRANSACTION DETAILS", "AMOUNT", "AVAILABLE BALANCE"]
            ]
        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 0])
            is_balance_col_empty = False
            if date_match and df.loc[j, 3] == "":
                # print("WHAT!!!")
                # print(df.loc[j,3])
                k = j + 1
                new_row = df.loc[j - 1] + df.loc[j]
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                while k < (len(df)) and not next_date_match and df.loc[k, 3] == "":
                    new_row += "\n" + df.loc[k]
                    j += 1
                    k += 1
                    if k < (len(df)):
                        next_date_match = re.search(date_pattern, df.loc[k, 0])
                merged_row.append(new_row)

            elif date_match:
                k = j + 1
                new_row = df.loc[j]
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                while k < (len(df)) and not next_date_match:
                    new_row += "\n" + df.loc[k]
                    j += 1
                    k += 1
                    if k < (len(df)):
                        next_date_match = re.search(date_pattern, df.loc[k, 0])
                merged_row.append(new_row)
            # else:

            j += 1
        df = pd.DataFrame(merged_row)
        df = df.apply(lambda x: x.str.replace("₹", ""))
        # print(df)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
