import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re
import matplotlib.pyplot as plt

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern22,
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# # Done
# # 7_ICICI_detailStatement_19-5-2021@11-44-35.pdf
# # FASHION.FORWARD.01.01.2023.TO.28.02.2023
# # pattern: "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
# def Pattern22(pdf_file, csv_output):
#     pattern_text = "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
#     if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
#         return

#     Bank_Name = "ICICI Bank"
#     extracting_utility.print_info(
#         inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
#     )

#     date_pattern = r"\d{2}-[A-Za-z]{3}-\n\d{4}"
#     tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
#     df_total = pd.DataFrame()
#     for i in tqdm(range(tables.n)):
#         df = tables[i].df
#         # Remove trailing backslashes from all cells
#         df = df.applymap(lambda x: x.rstrip("\/"))
#         j = 0
#         merged_row = []
#         if i == 0:
#             merged_row = [
#                 [
#                     "Sr No",
#                     "Value Date",
#                     "Transaction Date",
#                     "Cheque Number",
#                     "Transaction Remarks",
#                     "Debit Amount",
#                     "Credit Amount",
#                     "Balance(INR)",
#                 ]
#             ]

#         while j < (len(df)):
#             date_match = re.search(date_pattern, df.loc[j, 1])
#             if date_match:
#                 if "EP\n" in df.loc[j, 4]:
#                     df.loc[j, 4] = df.loc[j, 4].replace("EP\n", "")
#                 merged_row.append(df.loc[j])
#             j += 1
#         df = pd.DataFrame(merged_row)
#         df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)

#     df = df_total.drop_duplicates().reset_index(drop=True)
#     df.to_csv(csv_output, mode="a", index=False, header=False)

#     global Success
#     Success = True
#     return


# Done
# 7_ICICI_detailStatement_19-5-2021@11-44-35.pdf
# FASHION.FORWARD.01.01.2023.TO.28.02.2023
# pattern: "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
def Pattern22(pdf_file, csv_output):
    pattern_text = "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["85,156,230,285,361,418,483"]
    cols *= 128
    date_pattern = r"\d{2}-[A-Za-z]{3}-\n\d{4}"
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", row_tol=12, columns=cols
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='grid')
        # plt.show(block=True)
        df = df.applymap(lambda x: x.rstrip("\/"))
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)

    j = 0

    merged_row = [
        [
            "Sr No",
            "Value Date",
            "Transaction Date",
            "Cheque Number",
            "Transaction Remarks",
            "Debit Amount",
            "Credit Amount",
            "Balance(INR)",
        ]
    ]

    while j < (len(df_total)):
        date_match = re.search(date_pattern, df_total.loc[j, 1])
        if date_match:
            k = j + 1
            new_row = df_total.loc[j]
            while k < (len(df_total)):
                next_date_match = re.search(date_pattern, df_total.loc[k, 1])
                if next_date_match or df_total.loc[k, 0] != "":
                    break
                new_row += "\n" + df_total.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df = df.applymap(extracting_utility.remove_trailing_newline)
    df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)

    global Success
    Success = True
    return


def Default(pdf_file, csv_output):
    Bank_Name = "ICICI Bank"
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
