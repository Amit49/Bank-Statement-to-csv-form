import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern17,
        PatternUnion2,
        PatternUnion3,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 25_Union_Bank_1.8.2021 TO 31.3.2022.pdf
# pattern: "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
def Pattern17(pdf_file, csv_output):
    pattern_text = "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern17")

    Bank_Name = "Union Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["111,204,391,485,576"]
    cols *= 128
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", columns=cols)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [
                ["Tran Id", "Tran Date", "Remarks", "Amount (Rs.)", "Balance (Rs.)"]
            ]

        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 1])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                # print(f"Row:::\n{df.loc[j]}")
                if (
                    j + 1 < (len(df))
                    and df.loc[j + 1, 1] == ""
                    and df.loc[j + 1, 2] != ""
                ):
                    new_row = df.loc[j] + df.loc[j + 1]
                    # print(f"New Row:::\n{new_row}")
                    merged_row.append(new_row)
                    j += 2
                    continue
                else:
                    merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total = df_total.iloc[:, :5]
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True


# Done
# OpTransactionHistoryUX3_PDF02-12-2023_1701664948.pdf
# pattern: "Date Tran Id-1 Remarks UTR Number Instr. ID Withdrawals Deposits Balance"
def PatternUnion2(pdf_file, csv_output):
    pattern_text = (
        "Date Tran Id-1 Remarks UTR Number Instr. ID Withdrawals Deposits Balance"
    )
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Union Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["93,213,278,383,469,562,653"]
    cols *= 128
    TA = ["0,1106,750,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols, table_areas=TA,
        row_tol = 12
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        df = extracting_utility.filter_dataframe(df,1,"For any queries",2)
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df = extracting_utility.filter_dataframe(df,0,"Date",1,True)
    
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    
    merged_row = [
        [
            "Date",
            "Remarks",
            "Tran Id-1",
            "UTR Number",
            "Instr. ID",
            "Withdrawals",
            "Deposits",
            "Balance",
        ]
    ]
    
    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if(j==0):
            df.loc[j,0] = df.loc[j,0].replace("Date","")
            df.loc[j,1] = df.loc[j,1].replace("Remarks","")
            df.loc[j,2] = df.loc[j,2].replace("Tran Id-1","")
            df.loc[j,3] = df.loc[j,3].replace("UTR Number","")
            df.loc[j,4] = df.loc[j,4].replace("Instr. ID","")
            df.loc[j,5] = df.loc[j,5].replace("Withdrawals","")
            df.loc[j,6] = df.loc[j,6].replace("Deposits","")
            df.loc[j,7] = df.loc[j,7].replace("Balance","")
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if (next_date_match or df.loc[k,4]!=""):
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
# Statement__BHAV0110_1701501359_decrypt.pdf
# pattern: "S.No Date Transaction Id Remarks Amount(Rs.) Balance(Rs.)"
def PatternUnion3(pdf_file, csv_output):
    pattern_text = "S.No Date Transaction Id Remarks Amount(Rs.) Balance(Rs.)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Union Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(pdf_file,flavor="lattice",pages="all",line_scale = 20)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i],"line")
        df = extracting_utility.filter_dataframe(df,0,"Transaction",1)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df.loc[-1] = [
                "S.No",
                "Date",
                "Transaction Id",
                "Remarks",
                "Amount(Rs.)",
                "Balance(Rs.)",
            ]
    df.index = df.index + 1  # shifting index
    df.sort_index(inplace=True)
    # extracting_utility.print_markdown(df)
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return