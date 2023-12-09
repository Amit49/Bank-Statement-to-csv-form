import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import tabula
import re
import matplotlib.pyplot as plt

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern22,
        PatternICICI3,
        PatternICICI4,
        PatternICICI5,
        PatternICICI6,
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
        pdf_file, flavor="stream", pages="all", row_tol=12, columns=cols, edge_tol=500
    )
    # tables.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df = df.applymap(lambda x: x.rstrip("\/"))
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    # df_total.to_csv("csv_output.csv", mode="a", index=False, header=False)
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
            if df_total.loc[j,6] == "":
                split_text = df_total.loc[j,7].split(" ",1)
                df_total.loc[j,6] = split_text[0]
                df_total.loc[j,7] = split_text[1]
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
    if extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="w", index=False, header=False)

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

def extract_and_remove_text(input_string, strpart1, strpart2):
    start_index = input_string.find(strpart1)
    end_index = input_string.find(strpart2, start_index + len(strpart1))

    if start_index != -1 and end_index != -1:
        extracted_text = input_string[start_index + len(strpart1):end_index]
        input_string = input_string[:start_index] + input_string[end_index + len(strpart2):]
        return extracted_text, input_string
    else:
        return None, input_string

# TODO: Particles is up and down row of Date position
# make change in utils.py of camelot package
# 02. 01.06.2023 TO 31.07.2023.pdf
# pattern: "DATE MODE** PARTICULARS DEPOSITS WITHDRAWALS BALANCE"
def PatternICICI3(pdf_file, csv_output):
    pattern_text = "DATE MODE** PARTICULARS DEPOSITS WITHDRAWALS BALANCE"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    cols = ["73,153,382,436,525"]
    cols *= 128
    TA = ["0,800,600,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TA,
        # , row_tol=10
    )
    # tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    merged_row = [
        [
            "DATE",
            "MODE**",
            "PARTICULARS",
            "DEPOSITS",
            "WITHDRAWALS",
            "BALANCE",
        ]
    ]
    remaining_string = extracting_utility.text_in_pdf(pdf_file)
    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and len(df.loc[j])>5 and df.loc[j, 5]!= "":
            first_part = df.loc[j,0]
            last_part = ""
            if df.loc[j,1] != "":
                first_part = df.loc[j,1]
            if df.loc[j,3] != "":
                last_part = df.loc[j,3]
            else:
                last_part = df.loc[j,4]
                
            extracted_text, remaining_string = extract_and_remove_text(remaining_string, first_part, last_part)
            df.loc[j, 2] = extracted_text
            merged_row.append(df.loc[j])
        j += 1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# INFINITE_1_ICICI_APR TO JUNE 2023.pdf
# pattern: "Date Description Amount Type"
def PatternICICI4(pdf_file, csv_output):
    pattern_text = "Date Description Amount Type"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# SHILPA_1.4.2022 to 31.3.2023.pdf
# pattern: "Date Particulars Chq.No. Withdrawals Deposits Autosweep Reverse"
def PatternICICI5(pdf_file, csv_output):
    pattern_text = "Date Particulars Chq.No. Withdrawals Deposits Autosweep Reverse"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df = extracting_utility.filter_dataframe(df, 0, "Page Total", 2)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# AM_-_April_To_Aug_2023_1701073987.pdf
# pattern: "No. Transaction ID Value Date Txn Posted Date ChequeNo. Description Cr/Dr Transaction"
def PatternICICI6(pdf_file, csv_output):
    pattern_text = "No. Transaction ID Value Date Txn Posted Date ChequeNo. Description Cr/Dr Transaction"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["30,107,170,310,400,700,760,830"]
    cols *= 128
    TR = ["0,1340,910,0"]
    TR *= 128

    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR, row_tol=12
    )
    # tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}/\d{2}/\d{4}"

    merged_row = [
        [
            "No.",
            "Transaction ID",
            "Value Date",
            "Txn Posted Date",
            "ChequeNo.",
            "Description",
            "Cr/Dr",
            "Transaction Amount(INR)",
            "Available Balance(INR)",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 2])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 2])
                if (
                    next_date_match
                    or df.loc[k, 2] != ""
                    or df.loc[k, 3] != ""
                    or df.loc[k, 4] != ""
                ):
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
