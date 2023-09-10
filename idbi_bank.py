import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern5,
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 13_IDBI_2. 01.04.2021 to 13.10.2021.pdf
# pattern: "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
def Pattern5(pdf_file, csv_output):
    pattern_text = "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
    pattern_text1 = "Date Particulars Chq. no Withdrawals Deposits Balance"
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1):
        return
    Bank_Name = "IDBI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["37,83,345,432,496,559"]
    cols *= 128

    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all")
    should_end = False
    date_pattern = r"(\d{2})(-|/)(\d{2})(-|/)(\d{4})"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        if len(df.columns) > 2 and len(df.columns) < 6:
            df.insert(2, "Chq. no", "")

        merged_rows = []  # List to store the merged rows
        j = 0
        while j < len(df):
            date_match = re.search(date_pattern, df.loc[j, 0])
            if date_match and len(df.loc[j]) > 5:
                merged_rows.append(df.loc[j])
            elif (
                len(df.loc[j]) > 5
                and df.loc[j, 0] == ""
                and df.loc[j, 3] == ""
                and df.loc[j, 1] != ""
            ):
                merged_rows.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_rows)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    j = 0
    merged_row = [
        ["Date", "Particulars", "Chq. no", "Withdrawals", "Deposits", "Balance"]
    ]
    while j < (len(df_total)):
        date_match = re.search(date_pattern, df_total.loc[j, 0])
        if date_match:
            k = j + 1
            new_row = df_total.loc[j]
            if k < (len(df_total)):
                next_date_match = re.search(date_pattern, df_total.loc[k, 0])
            while k < (len(df_total)) and not next_date_match:
                new_row += "\n" + df_total.loc[k]
                j += 1
                k += 1
                if k < (len(df_total)):
                    next_date_match = re.search(date_pattern, df_total.loc[k, 0])
            merged_row.append(new_row)
        j += 1

    df = pd.DataFrame(merged_row)
    j = 0
    while j < len(df):
        if df.isnull().loc[j, 5]:
            df.loc[j, 5] = df.loc[j, 4]
            df.loc[j, 4] = df.loc[j, 3]
            df.loc[j, 3] = df.loc[j, 2]
            df.loc[j, 2] = ""
        j = j + 1
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


def Default(pdf_file, csv_output):
    Bank_Name = "IDBI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name,
        Bank_Name,
        extracting_utility.get_page_num(pdf_file),
    )

    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # Remove trailing backslashes from all cells
        df = df.applymap(lambda x: x.rstrip("\/"))
        df.to_csv(csv_output, mode="a", index=False, header=False)
    return
