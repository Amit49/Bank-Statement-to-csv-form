import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern19,
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


def Default(pdf_file, csv_output):
    Bank_Name = "Federal Bank"
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


# Done
# HIRVA 1.8 TO 6.8.pdf
# pattern: "TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
# pattern: "Date\nValue Date\nParticulars\nTran\nType\nCheque\nDetails\nWithdrawals\nDeposits\nBalance\nDr/Cr"
def Pattern19(pdf_file, csv_output):
    pattern_text1 = "TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
    pattern_text2 = "Date\nValue Date\nParticulars\nTran\nType\nCheque\nDetails\nWithdrawals\nDeposits\nBalance\nDr/Cr"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return
    # print("Pattern19")

    Bank_Name = "Federal Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    skip_first = True
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", line_scale=40)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        for index, row in df.iterrows():
            if "Date" in row[0]:
                if skip_first:
                    skip_first = False
                else:
                    df.drop(index, inplace=True)
                    break
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if  extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
