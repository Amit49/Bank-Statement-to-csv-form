import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False
Bank_Name = "Federal Bank"


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern19,
        PatternFederal1,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break

# Done
# HIRVA 1.8 TO 6.8.pdf
# pattern: "TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
# pattern: "Date\nValue Date\nParticulars\nTran\nType\nCheque\nDetails\nWithdrawals\nDeposits\nBalance\nDr/Cr"
def Pattern19(pdf_file, csv_output):
    pattern_text1 = "TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
    pattern_text2 = "Date\nValue Date\nParticulars\nTran\nType\nCheque\nDetails\nWithdrawals\nDeposits\nBalance\nDr/Cr"
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text1
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return
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
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 23640200000384_1701862034.pdf
# pattern: "Date ParticularsTran\nTypeCheque\nDetailsWithdrawals Deposits Cr/Dr Value Date\nOpening Balance CR 9051.64Balance Tran Id"
def PatternFederal1(pdf_file, csv_output):
    pattern_text = "Date ParticularsTran\nTypeCheque\nDetailsWithdrawals Deposits Cr/Dr Value Date\nOpening Balance CR 9051.64Balance Tran Id"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", line_scale=20)

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}-\d{2}-\d{4}"

    merged_row = [
        [
            "Date",
            "Value Date",
            "Particulars",
            "Tran Type",
            "Tran Id",
            "Cheque Details",
            "Withdrawals",
            "Deposits",
            "Balance",
            "Cr/Dr",
        ]
    ]

    j = 0
    not_skip = True
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if not_skip and "Opening Balance" in str(df.loc[j,2]) or "GRAND TOTAL" in str(df.loc[j,2]):
            new_row = df.loc[j]
            merged_row.append(new_row)
            not_skip = False
        elif date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if next_date_match or df.loc[k, 0] != "":
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return
