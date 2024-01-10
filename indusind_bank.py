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
        PatternIndusind2,
        PatternIndusind3,
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
    TA = ["0,805,580,85"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TA
    )
    last_df_row = pd.DataFrame()
    df_total = pd.DataFrame()

    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
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

    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates(subset=[0, 3, 4, 5]).reset_index(drop=True)
    # print(df_total)
    df_total = df_total.iloc[:, :6]
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 6_SEP-OCT_23_1701249149.pdf
# pattern: "DATE PARTICULARS CHQ.NO. WITHDRAWALS DEPOSITS BALANCE"
def PatternIndusind2(pdf_file, csv_output):
    pattern_text = "DATE PARTICULARS CHQ.NO. WITHDRAWALS DEPOSITS BALANCE"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "INDUSLAND BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    cols = ["102,345,430,600,750"]
    cols *= 128
    TR = ["0,835,870,0"]
    TR *= 128

    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR
    )
    # tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{2}"
    merged_row = [
        [
            "DATE",
            "PARTICULARS",
            "CHQ.NO.",
            "WITHDRAWALS",
            "DEPOSITS",
            "BALANCE",
        ]
    ]

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
                    or df.loc[k, 0] != ""
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
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# INDUSIND_BANK_-_010423_TO_071123_1701253918.pdf
# pattern: "Date Description Credit Type Debit\nBalance"
def PatternIndusind3(pdf_file, csv_output):
    pattern_text = "Date Description Credit Type Debit\nBalance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "INDUSLAND BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    cols = ["100,230,425,545,650"]
    cols *= 128
    TR = ["0,835,870,0"]
    TR *= 128

    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR
    )
    # tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    # tables.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        index_to_discard_before = df[
            df[5].str.contains("Balance", case=False, na=False)
        ].index
        index_to_discard_after = df[
            df[5].str.contains(r"Page.*of", case=False, na=False)
        ].index
        if not index_to_discard_before.empty:
            df = df.loc[index_to_discard_before[0] + 1 :]
        if not index_to_discard_after.empty:
            df = df.loc[: index_to_discard_after[0] - 1]
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total

    # Removing all rows before "OPENING BALANCE" and after "TRANSACTION TOTAL DR/CR:"
    # target_value_start = "OPENING BALANCE"
    # target_value_end = "TRANSACTION TOTAL DR/CR:"
    # index_to_discard_before = df[df[2].str.contains(target_value_start, case=False, na=False)].index
    # index_to_discard_after = df[df[0].str.contains(target_value_end, case=False, na=False)].index
    # if not index_to_discard_after.empty and not index_to_discard_before.empty:
    #     df = df.loc[index_to_discard_before[0] : index_to_discard_after[0] - 1]

    # date_pattern = r"\d{2} [A-Za-z]{3} \d{2}"
    date_pattern = r"(\d{2} [A-Za-z]{3} \d{2})|([A-Za-z]{3} \d{1,2}, \d{4})"
    merged_row = []

    j = len(df) - 1
    while j >= 0:
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            k = j - 1
            new_row = df.loc[j]
            while k >= 0:
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if (
                    next_date_match
                    or df.loc[k, 0] != ""
                    or df.loc[k, 3] != ""
                    or df.loc[k, 4] != ""
                ):
                    break
                new_row =  df.loc[k]+ "\n" + new_row  
                j -= 1
                k -= 1
            merged_row.append(new_row)
        j -= 1

    df = pd.DataFrame(merged_row)
    # Reverse the order of rows in the DataFrame
    df = df.iloc[::-1].reset_index(drop=True)
    # Adding the header
    df.loc[-1] = [
            "DATE",
            "Type",
            "Description",
            "Debit",
            "Credit",
            "Balance",
        ]
    df.index = df.index + 1  # shifting index
    df.sort_index(inplace=True)
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return
