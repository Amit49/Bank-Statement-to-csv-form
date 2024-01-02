import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import tabula
import re
import matplotlib.pyplot as plt

Success = False
Bank_Name = "ICICI Bank"

def initialize(pdf_file, csv_output):
    patterns = [
        Pattern22,
        PatternICICI3,
        PatternICICI4,
        PatternICICI5,
        PatternICICI6,
        PatternICICI7,
        PatternICICI8,
        PatternICICI9,
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

# 
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

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["85,156,230,285,361,418,490"]
    cols *= 128
    date_pattern = r"\d{2}-[A-Za-z]{3}-\n\d{4}"
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", row_tol=12, columns=cols, edge_tol=500
    )
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="guess", pages="1",
    #     line_scale = 20,
    # )
    # # tables.export('foo.csv', f='csv', compress=True)
    # combined_table = pd.concat([table.df for table in tables])
    # combined_table.to_csv('foo.csv', index=False)
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
        input_string = input_string[end_index + len(strpart2):]
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
    # df.to_csv("csv_output.csv", mode="w", index=False, header=False)
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
    df.to_csv(csv_output, mode="w", index=False, header=False)
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

# Done
# ConsolidatedStatementReport_Dec2023_1701766571.pdf
# pattern: "SR. NO. DATE TRANSACTION\nIDVALUE DATE PARTICULARS DEPOSITS WITHDRAWLS BALANCE"
def PatternICICI7(pdf_file, csv_output):
    pattern_text = "SR. NO. DATE TRANSACTION\nIDVALUE DATE PARTICULARS DEPOSITS WITHDRAWLS BALANCE"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = [""]
    cols *= 128
    TA = [""]
    TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TA
    # )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# icici_bank_1701412856.pdf
# pattern: "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount\n(INR )Deposit Amount\n(INR )Balance (INR )"
def PatternICICI8(pdf_file, csv_output):
    pattern_text = "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount\n(INR )Deposit Amount\n(INR )Balance (INR )"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["213,310,410,500,685,775,860"]
    cols *= 128
    TR = ["0,1340,950,0"]
    TR *= 128

    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR, row_tol=12
    )
    # tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    # tables.export("foo.csv",f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}/\d{2}/\d{4}"

    merged_row = [
        [
            "S No.",
            "Value Date",
            "Transaction Date",
            "Cheque Number",
            "Transaction Remarks",
            "Withdrawal Amount (INR)",
            "Deposit Amount (INR)",
            "Balance(INR)",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 1])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 1])
                if (
                    next_date_match
                    or df.loc[k, 2] != ""
                    or df.loc[k, 3] != ""
                ):
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

# TODO: need to make changes in
#       C:\Users\username\AppData\Local\Programs\Python\Python311\Lib\site-packages\PyPDF2\_cmap.py
'''
def parse_bfrange(
    l: bytes,
    map_dict: Dict[Any, Any],
    int_entry: List[int],
    multiline_rg: Union[None, Tuple[int, int]],
) -> Union[None, Tuple[int, int]]:
    lst = [x for x in l.split(b" ") if x]
    closure_found = False
    if multiline_rg is not None:
        fmt = b"%%0%dX" % (map_dict[-1] * 2)
        a = multiline_rg[0]  # a, b not in the current line
        b = multiline_rg[1]
        for sq in lst[1:]:
            if sq == b"]":
                closure_found = True
                break
            map_dict[
                unhexlify(fmt % a).decode(
                    "charmap" if map_dict[-1] == 1 else "utf-16-be",
                    "surrogatepass",
                )
            ] = unhexlify(sq).decode("utf-16-be", "surrogatepass")
            int_entry.append(a)
            a += 1
    else:
        a = int(lst[0], 16)
        b = int(lst[1], 16)
        nbi = max(len(lst[0]), len(lst[1]))
        map_dict[-1] = ceil(nbi / 2)
        fmt = b"%%0%dX" % (map_dict[-1] * 2)
        if lst[2] == b"[":
            for sq in lst[3:]:
                if sq == b"]":
                    closure_found = True
                    break
                map_dict[
                    unhexlify(fmt % a).decode(
                        "charmap" if map_dict[-1] == 1 else "utf-16-be",
                        "surrogatepass",
                    )
                ] = unhexlify(sq).decode("utf-16-be", "surrogatepass")
                int_entry.append(a)
                a += 1
        else:  # case without list
            c = int(lst[2], 16)
            fmt2 = b"%%0%dX" % max(4, len(lst[2]))
            closure_found = True
            while a <= b:
                map_dict[
                    unhexlify(fmt % a).decode(
                        "charmap" if map_dict[-1] == 1 else "utf-16-be",
                        "surrogatepass",
                    )
                ] = unhexlify(fmt2 % c).decode("utf-16-be", "surrogatepass")
                int_entry.append(a)
                a += 1
                c += 1
    return None if closure_found else (a, b)
'''
# DONE
# Statement_2023MTH11_168559138_unlocked_1701768364 (1).pdf
# pattern: "Tran D ateValu e Date Particulars Loca tion Chq.No Withdrawals Deposits Bala nce (INR)"
def PatternICICI9(pdf_file, csv_output):
    pattern_text = "Tran D ateValu e Date Particulars Loca tion Chq.No Withdrawals Deposits Bala nce (INR)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["68,103,286,374,407,455,506"]
    cols *= 128
    TA = ["0,820,570,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols, table_areas=TA,
        split_text = True
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df = extracting_utility.filter_dataframe(df,0,"Tran Date",1)
        df = extracting_utility.filter_dataframe(df,2,"Total",2)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}-\d{2}-\d{4}"

    merged_row = [
        [
            "Tran Date",
            "Value Date",
            "Particulars",
            "Location",
            "Chq.No",
            "Withdrawals",
            "Deposits",
            "Balance (INR).",
        ]
    ]
    for i in range(len(df)):
        date_match = re.search(date_pattern, df.loc[i, 0])
        if date_match:
            if  df.loc[i, 2] == "":
                if i > 0:
                    df.loc[i, 2] = df.loc[i-1, 2]
                    df.loc[i - 1, 2] = ""
    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if (
                    next_date_match
                    or df.loc[k, 1] != ""
                    or df.loc[k, 3] != ""
                    or df.loc[k, 4] != ""
                    or df.loc[k, 7] != ""
                ):
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df = df.iloc[:, :8]
    # print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return