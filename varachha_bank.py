import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern18,
        PatternVarachha2,
        PatternVarachha3,
        PatternVarachha4,
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 26_VARCHHA BANK_01.04.2021 TO 31.03.2022.pdf
# pattern: "TRN. Date | Value Date | Narration Chq/Ref.No Debit Credit} Closing Bal"
def Pattern18(pdf_file, csv_output):
    pattern_text = (
        r"TRN.*Date.*Value Date.*Narration.*Chq/Ref\.No.*Debit.*Credit.*Closing Bal"
    )
    if not re.search(pattern_text, extracting_utility.text_in_pdf(pdf_file)):
        return
    # print("Pattern18")

    Bank_Name = "VARCHHA BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    cols = ["90,148,300,368,435,500"]
    cols *= 128
    TA = ["0,750,574,0"]
    TA *= 128
    tables_first_page = camelot.read_pdf(
        pdf_file,
        flavor="stream",
        pages="1",
        row_tol=20,
        # edge_tol = 150,
        # split_text=True,
        columns=cols,
        table_areas=TA,
    )
    # tables_first_page.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables_first_page.n)):
        df = tables_first_page[i].df
        # extracting_utility.show_plot_graph(tables_first_page[i])
        date_pattern = r"\d{2}-\d{2}-\d{4}"
        pattern = r"\|"
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [
                [
                    "TRN.  Date",
                    "Value  Date",
                    "Narration",
                    "Chq/Ref.No",
                    "Debit",
                    "Credit",
                    "Closing  Bal",
                ]
            ]

        while j < (len(df)):
            match_ = re.search(pattern, df.loc[j, 0])
            date_match = re.search(date_pattern, df.loc[j, 0])
            date_match_2 = re.search(date_pattern, df.loc[j, 1])

            if date_match:
                if match_:
                    str1 = df.loc[j, 0][: match_.start()]
                    str2 = df.loc[j, 0][match_.start() + 1 :]
                    df.loc[j, 0] = str1
                    df.loc[j, 1] = str2
                elif len(df.loc[j, 1]) > 10:
                    str1 = df.loc[j, 1][:10]
                    str2 = df.loc[j, 1][10:] + df.loc[j, 2]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                elif len(df.loc[j, 1]) < 1:
                    str1 = df.loc[j, 2][:10]
                    str2 = df.loc[j, 2][10:]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                if "OPENING" in df.loc[j, 1] or "CLOSING" in df.loc[j, 1]:
                    df.loc[j, 2] = df.loc[j, 1] + df.loc[j, 2]
                    df.loc[j, 1] = ""

                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    # print(df_total.to_string())
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages=f"2-{extracting_utility.Page_Num}")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        date_pattern = r"\d{2}-\d{2}-\d{4}"
        pattern = r"\|"
        j = 0
        merged_row = []
        # if i == 0:
        #     merged_row = [
        #         [
        #             "TRN.  Date",
        #             "Value  Date",
        #             "Narration",
        #             "Chq/Ref.No",
        #             "Debit",
        #             "Credit",
        #             "Closing  Bal",
        #         ]
        #     ]

        while j < (len(df)):
            match_ = re.search(pattern, df.loc[j, 0])
            date_match = re.search(date_pattern, df.loc[j, 0])
            date_match_2 = re.search(date_pattern, df.loc[j, 1])

            if date_match:
                if match_:
                    str1 = df.loc[j, 0][: match_.start()]
                    str2 = df.loc[j, 0][match_.start() + 1 :]
                    df.loc[j, 0] = str1
                    df.loc[j, 1] = str2
                elif len(df.loc[j, 1]) > 10:
                    str1 = df.loc[j, 1][:10]
                    str2 = df.loc[j, 1][10:] + df.loc[j, 2]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                elif len(df.loc[j, 1]) < 1:
                    str1 = df.loc[j, 2][:10]
                    str2 = df.loc[j, 2][10:]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                if "OPENING" in df.loc[j, 1] or "CLOSING" in df.loc[j, 1]:
                    df.loc[j, 2] = df.loc[j, 1] + df.loc[j, 2]
                    df.loc[j, 1] = ""

                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if  extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True


def Default(pdf_file, csv_output):
    Bank_Name = "VARCHHA BANK"
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

# Done
# Detail03-Dec-2023-06-27-10-PM_1701674694_decrypt.pdf
# pattern: "DateValue DateNarrationChq/Ref. NoDebitCreditClosing Bal"
def PatternVarachha2(pdf_file, csv_output):
    pattern_text = "DateValue DateNarrationChq/Ref. NoDebitCreditClosing Bal"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "VARCHHA BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = [""]
    cols *= 128
    TA = [""]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all"
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df = extracting_utility.filter_dataframe(df,0,"Date",1)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# Detail03-Dec-2023-06-27-10-PM_1701674694_decrypt.pdf
# pattern: "Date Narration Cheque\nNo./Ref.NoWithdrawal Deposit Balance"
def PatternVarachha3(pdf_file, csv_output):
    pattern_text1 = "Date Narration Cheque\nNo./Ref.NoWithdrawal Deposit Balance"
    pattern_text2 = "Date Narration Cheque No./Ref.No Withdrawal Deposit Balance"
    if(
        not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1) and 
        not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2)
    ):
        return

    Bank_Name = "VARCHHA BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all"
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df = extracting_utility.filter_dataframe(df,1,"Narration",1,True)
    # print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# nov_23_cc_1701409030.pdf
# pattern: "Date Narration Cheque/Ref No Debit Credit Closing Bal"
def PatternVarachha4(pdf_file, csv_output):
    pattern_text = "Date Narration Cheque/Ref No Debit Credit Closing Bal"
    if(
        not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text)
    ):
        return

    Bank_Name = "VARCHHA BANK"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all"
    )
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
            "Narration",
            "Cheque/Ref No",
            "Debit",
            "Credit",
            "Closing Bal",
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