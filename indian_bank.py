import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False
Bank_Name = "Indian Bank"


def initialize(pdf_file, csv_output):
    patterns = [
        PatternIndian1,
        PatternIndian2,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# Statement_Pas-20126413166_1701170869_decrypt.pdf
# pattern: "TRANSACTION\nDATEPARTICULARS WITHDRAWALS DEPOSIT BALANCE"
def PatternIndian1(pdf_file, csv_output):
    pattern_text = "DATEPARTICULARS WITHDRAWALS DEPOSIT BALANCE"
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

    date_pattern = r"\d{2}/\d{2}/\d{4}"

    merged_row = [
        [
            "TRANSACTION DATE",
            "PARTICULARS",
            "WITHDRAWALS",
            "DEPOSIT",
            "BALANCE",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and df.loc[j, 4] != "":
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

    # print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return


# Done
# StatementOfAccount_50514369755_30112023_143659_1701335254.pdf
# pattern: "Value\nDatePost\nDateRemitter\nBranchDescription Cheque No DR CR Balance"
def PatternIndian2(pdf_file, csv_output):
    pattern_text = (
        "Value\nDatePost\nDateRemitter\nBranchDescription Cheque No DR CR Balance"
    )
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all",split_text=True)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i],"joint")
        # extracting_utility.show_plot_graph(tables[i],"line")
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total

    date_pattern = r"\d{2}/\d{2}\n/\d{4}"

    merged_row = [
        [
            "Value Date",
            "Post Date",
            "Remitter Branch",
            "Description",
            "Cheque No",
            "DR",
            "CR",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and df.loc[j, 7] != "":
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

    print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return
