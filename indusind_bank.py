import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern7,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 15_INDUSLAND BANK_01.04.2021 TO 31.03.2022.pdf
# pattern: "Date\nParticulars\nChq./Ref. No\nWithDrawal\nDeposit\nBalance"
def Pattern7(pdf_file, csv_output):
    pattern_text = "Date\nParticulars\nChq./Ref. No\nWithDrawal\nDeposit\nBalance"
    pattern_text1 = "Date Particulars Chq./Ref.No. Withdrawl Deposit Balance"
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1):
        return

    Bank_Name = "INDUSLAND BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["85,250,330,405,495,570"]
    cols *= 128
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", columns=cols)
    last_df_row = pd.DataFrame()
    df_total = pd.DataFrame()

    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='textedge')
        # plt.show(block=True)
        merged_rows = []  # List to store the merged rows
        prev_row = None
        date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
        ignore = False
        for index, row in df.iterrows():
            date_match = re.search(date_pattern, row[0])
            if "For any queries of details" in row[1]:
                ignore = True
                continue
            if date_match:
                ignore = False
            if ignore:
                continue
            if row[0] == "":
                # Merge with the previous row
                if prev_row is not None:
                    prev_row[1] += "\n" + row[1]
            else:
                # Add the row to the list of merged rows
                merged_rows.append(row)
                prev_row = row

        df = pd.DataFrame(merged_rows)
        for index, row in df.iterrows():
            if "Date" not in row[0] and not re.search(date_pattern, row[0]):
                df = df.drop(index)
        j = 0
        df = df.reset_index(drop=True)
        # print(df)
        while j < len(df):
            if (
                not last_df_row.empty
                and df.loc[j, 0] == (last_df_row[0])
                and df.loc[j, 2] == (last_df_row[2])
                and df.loc[j, 5] == (last_df_row[5])
            ):
                df = df.drop([j]).reset_index(drop=True)
            if df.empty:
                break
            if j < len(df):
                last_df_row = df.loc[j]
            j += 1
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)

    if  extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates(subset=[0, 3, 4, 5]).reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
