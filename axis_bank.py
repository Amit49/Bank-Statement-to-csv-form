import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern2,
        PatternAxis2,
        PatternAxis3,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 2_axis_1. 01-04-2021 to 13-10-2021.pdf
# 2b_2. AXIS BANK.pdf
# pattern: "Tran Date Chq No Particulars Debit Credit Balance Init."
def Pattern2(pdf_file, csv_output):
    pattern_text = "Tran Date Chq No Particulars Debit Credit Balance Init"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Axis Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    column_name_appened = False
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", line_scale=40)
    df_total = pd.DataFrame()
    shouldBreak = False
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        for index, row in df.iterrows():
            if "Charge Type" in row[3]:
                shouldBreak = True
                break
            match = re.search(r"[a-zA-Z]", row[1])
            if match:
                year = match.group(0)
                updated_string = row[1][: match.start()]
                remainder = row[1][match.start() :]
                row[1] = updated_string
                row[2] = remainder + row[2]
            if row[3] == "" and row[4] == "" and row[0] != "":
                # Find the last space's position
                last_space_index = row[2].rfind(" ")

                # Extract text from the last space to the end
                row[3] = row[2][last_space_index + 1 :]
                row[2] = row[2][:last_space_index]
        if column_name_appened is False:
            column_name_appened = True
            df = df.drop(0)
            df.loc[-1] = [
                "Tran Date",
                "Chq No",
                "Particulars",
                "Debit",
                "Credit",
                "Balance",
                "Init. br",
            ]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True)
        if shouldBreak:
            break
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    # tables[i].to_csv(csv_output ,mode='a')
    global Success
    Success = True
    return


# Done
# Account_stmt_1701169154.pdf
# pattern: "Tran Date Value Date Transaction Particulars Chq No Amount(INR) DR/CR Balance(INR) Branch Name"
def PatternAxis2(pdf_file, csv_output):
    pattern_text = "Tran Date Value Date Transaction Particulars Chq No Amount(INR) DR/CR Balance(INR) Branch Name"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Axis Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    # cols = ["76,115,291,340,395,430,475"]
    # cols *= 128
    # TR = ["0,825,580,0"]
    # TR *= 128

    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR
    # )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total

    # Removing all rows after "CLOSING BALANCE"
    target_value = "CLOSING BALANCE"
    index_to_discard_after = df[df[2] == target_value].index
    if not index_to_discard_after.empty:
        df = df.loc[: index_to_discard_after[0]]

    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# BANK_STATEMENT_1701249478.pdf
# pattern: "Tran Date Value  Date   Transaction Details Chq. No. Amount (In Rs.) Dr/Cr Balance (In Rs.) Branch Name"
def PatternAxis3(pdf_file, csv_output):
    pattern_text = "Tran Date Value  Date   Transaction Details Chq. No. Amount (In Rs.) Dr/Cr Balance (In Rs.) Branch Name"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Axis Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    # cols = ["68,120,318,360,420,450,508"]
    # cols *= 128
    # TR = ["0,800,580,0"]
    # TR *= 128

    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TR
    # )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")

    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total

    # Removing all rows before "OPENING BALANCE" and after "TRANSACTION TOTAL DR/CR:"
    target_value_start = "OPENING BALANCE"
    target_value_end = "TRANSACTION TOTAL DR/CR:"
    index_to_discard_before = df[df[2].str.contains(target_value_start, case=False, na=False)].index
    index_to_discard_after = df[df[0].str.contains(target_value_end, case=False, na=False)].index
    if not index_to_discard_after.empty and not index_to_discard_before.empty:
        df = df.loc[index_to_discard_before[0] : index_to_discard_after[0] - 1]

    df = df.applymap(lambda x: x.replace('  ', '$$'))
    df = df.applymap(lambda x: x.replace(' ', ''))
    df = df.applymap(lambda x: x.replace('$$', ' '))

    # Adding the header
    df.loc[-1] = [
                "Tran Date",
                "Value Date",
                "Transaction Details",
                "Chq. No.",
                "Amount (In Rs.)",
                "Dr/Cr",
                "Balance (In Rs.)",
                "Branch Name",
            ]
    df.index = df.index + 1  # shifting index
    df.sort_index(inplace=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
