import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern4,
        PatternSBI2,
        PatternSBI3,
        PatternSBI4,
        PatternSBI5,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 10_SBI_2. 1.6.2021 to 20.7.2021 OK.pdf
# 10_1_1. SBI.pdf
# pattern: "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
# pattern: "Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
def Pattern4(pdf_file, csv_output):
    pattern_text1 = "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
    pattern_text2 = (
        "Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
    )
    if not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text1
    ) and not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    # print("Pattern4")
    global Success

    if extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all", joint_tol=20)
        df_total = pd.DataFrame()
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            # camelot.plot(tables[i], kind='grid')
            # plt.show(block=True)
            df = df.drop(0)
            if i == 0:
                df.loc[-1] = [
                    "Txn Date",
                    "Value Date",
                    "Description",
                    "Ref No./Cheque No.",
                    "Branch Code",
                    "Debit",
                    "Credit",
                    "Balance",
                ]  # adding a row
                df.index = df.index + 1  # shifting index
                df.sort_index(inplace=True)
            df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
        if  extracting_utility.get_duplicate_remove():
            df_total = df_total.drop_duplicates().reset_index(drop=True)
        df_total.to_csv(csv_output, mode="a", index=False, header=False)
        Success = True
    # 10_1_1. SBI.pdf
    if extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text2):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
        df_total = pd.DataFrame()
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            if i != 0:
                df = df.drop(0)

            # # print("Pattern4222")
            for index, row in df.iterrows():
                match = re.search(r"\s\d{4}", row[1])
                if match:
                    year = match.group(0)
                    updated_string = row[1][: match.start()] + year
                    remainder = row[1][match.end() :]
                    # print(f"index:: {index}")
                    # print("_____")
                    # print(match.start())
                    # print(match.end())
                    # print("_____")
                    # print(row[1])
                    # print(row[2])
                    # print("_____")
                    # print(updated_string)
                    # print("_____")
                    # print(remainder)
                    row[1] = updated_string
                    row[2] = remainder + row[2]
                    # print("_____")
                    # print(row[1])
                    # print(row[2])
                elif row[1] == "":
                    match = re.search(r"\s\d{4}", row[2])
                    year = match.group(0)
                    updated_string = row[2][: match.end()]
                    remainder = row[2][match.end() :]
                    row[1] = updated_string
                    row[2] = remainder
            df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
        if  extracting_utility.get_duplicate_remove():
            df_total = df_total.drop_duplicates().reset_index(drop=True)
        df_total.to_csv(csv_output, mode="a", index=False, header=False)
        Success = True
    return

# Done
# Account_Statement_from_1_Oct_2023_to_31_Oct_2023_1701060585.pdf
# pattern: "Txn Date Value Date Description Ref No./Cheque\nNo.Branch\nCodeDebit Credit Balance"
def PatternSBI2(pdf_file, csv_output):
    pattern_text = "Txn Date Value Date Description Ref No./Cheque\nNo.Branch\nCodeDebit Credit Balance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # cols = [""]
    # cols *= 128
    # TA = [""]
    # TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all", columns=cols, table_areas=TA
    # )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all",
    )
    # tables.export('foo.csv',f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"\d{2}/\d{2}/\d{4}"
    merged_row = [
        [
            "Txn Date",
            "Value Date",
            "Description",
            "Ref No./Cheque No.",
            "Branch Code",
            "Debit",
            "Credit",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            value_date_match = re.search(date_pattern, df.loc[j, 1])
            if not value_date_match:
                split_row = df.loc[j,2].split(maxsplit=1)
                df.loc[j, 1] = split_row[0] 
                df.loc[j, 2] = split_row[1]
            elif len(df.loc[j, 1]) > 12:
                split_row = df.loc[j,1].split(maxsplit=1)
                df.loc[j, 1] = split_row[0]
                df.loc[j, 2] = split_row[1] + df.loc[j, 2]
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
    df = df.iloc[:, :8]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# NIRMYA_10. JANUARY 2023.pdf
# pattern: "Date Transaction Reference Ref.No./Chq.No. Credit Debit Balance"
def PatternSBI3(pdf_file, csv_output):
    pattern_text = "Date Transaction Reference Ref.No./Chq.No. Credit Debit Balance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # cols = [""]
    # cols *= 128
    # TA = [""]
    # TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all",
    #     # columns=cols, table_areas=TA
    # )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all",
        line_scale = 80
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    # df.to_csv("csv_output.csv", mode="w", index=False, header=False)
    
    date_pattern = r"\d{2}-\d{2}-\d{2}"
    merged_row = [
        [
            "Date",
            "Transaction Reference",
            "Ref.No./Chq.No.",
            "Credit",
            "Debit",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and len(df.loc[j])>5 and df.loc[j, 5]!= "":
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
    df = df.iloc[:, :6]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# NISHKAM_15.04.2022 TO 05.04.2023.pdf
# pattern: "Txn Date Value Date DescriptionRef/Cheque\nNo.Debit Credit Balance"
def PatternSBI4(pdf_file, csv_output):
    pattern_text = "Txn Date Value Date DescriptionRef/Cheque\nNo.Debit Credit Balance"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # cols = [""]
    # cols *= 128
    # TA = [""]
    # TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all",
    #     # columns=cols, table_areas=TA
    # )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all",
        # line_scale = 80
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    # df.to_csv("csv_output.csv", mode="w", index=False, header=False)
    
    date_pattern = r"\d{2}-\d{2}-\d{2}"
    merged_row = [
        [
            "Txn Date",
            "Value Date",
            "Description",
            "Ref/Cheque No.",
            "Debit",
            "Credit",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and len(df.loc[j])>6 and df.loc[j, 6]!= "":
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
    df = df.iloc[:, :7]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return

# Done
# 
# pattern: "Date Credit Balance DetailsRef No./Cheque"
def PatternSBI5(pdf_file, csv_output):
    pattern_text = "Date Credit Balance DetailsRef No./Cheque"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "State Bank of India (SBI)"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # cols = [""]
    # cols *= 128
    # TA = [""]
    # TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file, flavor="stream", pages="all",
    #     # columns=cols, table_areas=TA
    # )
    tables = camelot.read_pdf(
        pdf_file, flavor="lattice", pages="all",
        line_scale = 20,
        process_background=True,
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # print(df.to_markdown())
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    # df.to_csv("csv_output.csv", mode="w", index=False, header=False)
    
    date_pattern = r"\d{2} [A-Za-z]{3} \d{4}"
    merged_row = [
        [
            "Date",
            "Details",
            "Ref No./Cheque No",
            "Debit",
            "Credit",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and len(df.loc[j])>5 and df.loc[j, 5]!= "":
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
    df = df.iloc[:, :6]
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return