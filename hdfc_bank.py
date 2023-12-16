import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False
Bank_Name = "HDFC Bank"

def initialize(pdf_file, csv_output):
    patterns = [
        Pattern8,
        PatternHDFC1,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# HORIZON HIGH ~ HDFC ok.pdf
# pattern: "Date Narration Chq./Ref.No. Value Dt Withdrawal Amt. Deposit Amt. Closing Balance"
def Pattern8(pdf_file, csv_output):
    pattern_text = "Date Narration Chq./Ref.No. Value Dt Withdrawal Amt. Deposit Amt. Closing Balance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    cols = ["68,270,361,403,481,562,630"]
    cols *= 128
    TA = ["0,630,635,60"]
    TA *= 128
    should_start_ignore = False
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="44", columns=cols, edge_tol=500
    # )
    # tables.export('foo.csv', f='csv')
    date_pattern = r"\d{2}/\d{2}/\d{2}"
    df_total = pd.DataFrame()
    already_extracted = []
    start_page = 1
    end_page = extracting_utility.Page_Num
    # start_page = 38
    # end_page = 38
    page = start_page
    while page <= end_page:
        tables = camelot.read_pdf(
            pdf_file,
            flavor="stream",
            pages=f"{page}",
            columns=cols,
            split_text=True,
            # edge_tol=500,
            table_areas=TA,
        )
        # tables.export('foo.csv', f='csv')
        # larger_table = pd.DataFrame()
        for i in range(tables.n):
            # extracting_utility.show_plot_graph(tables[i])
            # print(tables[i])
            if(i==0):
                larger_table = tables[i]
            else:
                if tables[i].shape[0]*tables[i].shape[1] > larger_table.shape[0]*larger_table.shape[1]:
                    larger_table = tables[i]
        df_total = pd.concat([df_total, larger_table.df], axis=0).reset_index(drop=True)
        page = page + 1

    # for i in tqdm(range(tables.n)):
    #     df = tables[i].df
    #     print(type(tables[i]))
    #     extracting_utility.show_plot_graph(tables[i])
    #     if tables[i].page in already_extracted:
    #         continue
    #     already_extracted.append(tables[i].page)
    #     df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
    j = 0

    merged_row = []
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            if df.loc[j, 6] == "":
                j += 1
                continue
            if len(df.loc[j, 0]) > 8:
                df.loc[j, 1] = df.loc[j, 0][8:] + df.loc[j, 1]
                df.loc[j, 0] = df.loc[j, 0][0:8]
            merged_row.append(df.loc[j])
            j += 1
            continue
        elif df.loc[j, 0] == "" and df.loc[j, 2] == "" and df.loc[j, 1] != "":
            merged_row.append(df.loc[j])
            j += 1
            continue
        j += 1

    df_total = pd.DataFrame(merged_row).reset_index(drop=True)

    # df_total = df_total.drop_duplicates(subset=[0, 1, 2, 3, 4, 5, 6], keep="last").reset_index(
    #     drop=True
    # )
    j = 0
    merged_row = [
        [
            "Date",
            "Narration",
            "Chq./Ref.No.",
            "Value Dt",
            "Withdrawal Amt.",
            "Deposit Amt.",
            "Closing Balance",
        ]
    ]
    while j < (len(df_total)):
        date_match = re.search(date_pattern, df_total.loc[j, 0])
        if date_match and df_total.loc[j, 6] != "":
            k = j + 1
            new_row = df_total.loc[j]
            if k < (len(df_total)):
                next_date_match = re.search(date_pattern, df_total.loc[k, 0])
            while k < (len(df_total)) and not next_date_match:
                if (
                    "This is a computer generated statement" in df_total.loc[k, 5]
                    or "STATEMENT SUMMARY" in df_total.loc[k, 1]
                ):
                    break
                new_row += "\n" + df_total.loc[k]
                j += 1
                k += 1
                if k < (len(df_total)):
                    next_date_match = re.search(date_pattern, df_total.loc[k, 0])
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df = df.applymap(extracting_utility.remove_trailing_newline)
    if extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates(subset=[0, 2, 3, 4, 5, 6], keep="last").reset_index(
            drop=True
        )
    df = df.iloc[:, :7]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# BSF_2_1702290767.pdf
# pattern: "Date Narration Cheque/Ref. No. Value Date Withdrawal Deposit Closing"
def PatternHDFC1(pdf_file, csv_output):
    pattern_text = "Date Narration Cheque/Ref. No. Value Date Withdrawal Deposit Closing"
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
    date_pattern = r"\d{2} [A-Za-z]{3} \d{4}"

    merged_row = [
        [
            "Date",
            "Narration",
            "Cheque/Ref. No.",
            "Value Date",
            "Withdrawal",
            "Deposit",
            "Closing Balance",
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
