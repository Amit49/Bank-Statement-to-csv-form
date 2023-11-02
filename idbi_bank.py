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
        Pattern23,
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
    cols = ["83,280,345,432,496"]
    cols *= 128
    TR = ['0,846,634,0']
    TR *=128

    # tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all")
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all",columns=cols,table_areas = TR)
    # tables.export('foo.csv', f='csv')
    should_end = False
    date_pattern = r"(\d{2})(-|/)(\d{2})(-|/)(\d{4})"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        if should_end:
            break
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        if len(df.columns) > 2 and len(df.columns) < 6:
            df.insert(2, "Chq. no", "")

        merged_rows = []  # List to store the merged rows
        j = 0
        while j < len(df):
            if (len(df.loc[j])>4 and "Balance as on" in df.loc[j,4]):
                should_end = True
                break

            date_match = re.search(date_pattern, df.loc[j, 0])
            if "Our Toll-free numbers" in df.loc[j, 0]:
                break
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
    # Convert specific columns to strings
    columns_to_convert = [0, 1, 2, 3, 4, 5]
    df[columns_to_convert] = df[columns_to_convert].astype(str)
    df[columns_to_convert] = df[columns_to_convert].applymap(
        extracting_utility.remove_trailing_newline
    )
    # df = df.drop_duplicates().reset_index(drop=True)
    # # Find duplicate rows
    # duplicate_rows = df[df.duplicated(subset=[0, 2, 3, 4, 5], keep=False)]
    # need_to_remove = []
    # i = 0
    # while i < len(duplicate_rows.index):
    #     if (duplicate_rows.index[i + 1] - duplicate_rows.index[i]) < 2:
    #         if len(df.iloc[duplicate_rows.index[i]][1]) > len(
    #             df.iloc[duplicate_rows.index[i + 1]][1]
    #         ):
    #             need_to_remove.append(duplicate_rows.index[i + 1])
    #         else:
    #             need_to_remove.append(duplicate_rows.index[i])
    #     i += 2
    # print(need_to_remove)
    # df.drop(df.index[need_to_remove], inplace=True)
    # df.to_csv("duplicate_rows.csv", index=False, header=False)
    df = df.iloc[:, :6]
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# HB.4.11.11.2021.TO.31.3.2022.pdf
# pattern: "Txn Date Value DateCheque\nNoDescription CR/DRCC\nYSrl Balance (INR) Amount (INR)"
def Pattern23(pdf_file, csv_output):
    pattern_text = "Txn Date Value DateCheque\nNoDescription CR/DRCC\nYSrl Balance (INR) Amount (INR)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "IDBI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    date_pattern = r"\d{2}/\d{2}/\d{4}"
    # cols = ["62,152,201,405,445,476,500,564"]
    # cols *= 128
    # TR = ['0,846,634,0']
    # TR *= 10
    # tables = camelot.read_pdf(
    #     pdf_file,
    #     flavor="stream",
    #     pages="all",
    #     # columns=cols,
    #     table_regions=TR,
    #     edge_tol=500,
    #     split_text=True,
    # )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", line_scale = 100)
    # tables.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    j = 0
    merged_row = [
        [
            "Srl",
            "Txn Date",
            "Value Date",
            "Description",
            "Cheque No.",
            "CR/DR",
            "CCY",
            "Amount(INR)",
            "Balance(INR)",
        ]
    ]
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 1])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 1])
                if next_date_match or df.loc[k, 0] != "":
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    # df =df.applymap(extracting_utility.remove_trailing_newline)
    if extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates().reset_index(drop=True)
    df = df.iloc[:, :9]
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
