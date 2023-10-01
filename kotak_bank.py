import inspect
import os
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import tabula
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern10,
        Pattern11,
        Pattern12,
        Pattern13,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 18_kotak ok.pdf
# pattern: "Date Narration Chq/Ref No. Withdrawal (Dr) Deposit (Cr) Balance"
# pattern: "Date Narration Chq /Ref. No Withdrawal(Dr) Deposit(Cr) Balance"
def Pattern10(pdf_file, csv_output):
    pattern_text = (
        r"Date.*Narration.*Chq.*Ref.*No.*Withdrawal.*(Dr).*Deposit.*(Cr).*Balance"
    )
    # pattern_text_1 = "Date Narration Chq/Ref. No Withdrawal (Dr) Deposit (Cr) Balance"
    if not re.search(pattern_text, extracting_utility.text_in_pdf(pdf_file)):
        return
    # print("Pattern10")

    Bank_Name = "Kotak Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
    date_pattern_2 = r"\d{2}-[A-Za-z]{3}-\d{2}"
    ##### START
    cols = ["85,268,355,443,527,601"]
    cols *= 128
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all",columns=cols,split_text=True)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    j = 0
    merged_row = [
        [
            "Date",
            "Narration",
            "Chq/Ref No.",
            "Withdrawal (Dr)",
            "Deposit (Cr)",
            "Balance",
        ]
    ]
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        date_match_2 = re.search(date_pattern_2, df.loc[j, 0])
        if date_match or date_match_2:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                next_date_match_2 = re.search(date_pattern_2, df.loc[k, 0])
                if next_date_match or df.loc[k, 0] != "" or df.loc[k, 4] != "":
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    df =df.applymap(extracting_utility.remove_trailing_newline)
    # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
    ##### END
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="1",col_tol=10)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file, "temp.csv", output_format="csv", pages="all")
    # Delimiter
    # data_file_delimiter = ","

    # The max column count a line in the file could have
    # largest_column_count = 0

    # Loop the data lines
    # with open("temp.csv", "r") as temp_f:
    #     # Read the lines
    #     lines = temp_f.readlines()

    #     for l in lines:
    #         # Count the column count for the current line
    #         column_count = len(l.split(data_file_delimiter)) + 1

    #         # Set the new most column count
    #         largest_column_count = (
    #             column_count
    #             if largest_column_count < column_count
    #             else largest_column_count
    #         )

    # # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
    # column_names = [i for i in range(0, largest_column_count)]
    # df = pd.read_csv("temp.csv", names=column_names)
    # # print(df)
    # os.remove("temp.csv")
    # drop_row = []
    # j = 0
    # merged_row = [
    #     [
    #         "Date",
    #         "Narration",
    #         "Chq/Ref No.",
    #         "Withdrawal (Dr)",
    #         "Deposit (Cr)",
    #         "Balance",
    #     ]
    # ]
    # while j < (len(df)):
    #     if type(df.loc[j, 0]) != str:
    #         j += 1
    #         continue
    #     date_match = re.search(date_pattern, df.loc[j, 0])
    #     date_match_2 = re.search(date_pattern_2, df.loc[j, 0])
    #     if date_match or date_match_2:
    #         merged_row.append(df.loc[j])
    #     j += 1
    # df = pd.DataFrame(merged_row)
    if extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates().reset_index(drop=True)
    df = df.iloc[:, :6]
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 19_kotak_01. 01.04.2022 TO 31.08.2022.pdf
# pattern: "# TRANSACTION TRANSACTION DETAILS CHQ / REF NO. DEBIT(₹) CREDIT(₹) BALANCE(₹)"
def Pattern11(pdf_file, csv_output):
    pattern_text = (
        "# TRANSACTION TRANSACTION DETAILS CHQ / REF NO. DEBIT(₹) CREDIT(₹) BALANCE(₹)"
    )
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern11")

    Bank_Name = "Kotak Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", row_tol=15)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2} [A-Za-z]{3} \d{4}"
        drop_row = []
        for index, row in df.iterrows():
            date_match = re.search(date_pattern, row[1])
            if not date_match:
                drop_row.append(index)
        # print(drop_row)
        df.drop(drop_row, inplace=True)
        # print(df.columns)
        if len(df.columns) > 6 and column_name_appened is False:
            column_name_appened = True
            df.loc[-1] = [
                "#",
                "TRANSACTION",
                "TRANSACTION DETAILS",
                "CHQ / REF NO.",
                "DEBIT",
                "CREDIT",
                "BALANCE",
            ]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 20_kotak_2_1. 01.04.2021 TO 26.08.2021.PDF
# pattern: "Date Narration Withdrawal (Dr)/\nDeposit (Cr)Balance Chq/Ref"
def Pattern12(pdf_file, csv_output):
    pattern_text = "Date Narration Withdrawal (Dr)/\nDeposit (Cr)Balance Chq/Ref"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern12")

    Bank_Name = "Kotak Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", edge_tol=500)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    # print(tables.n)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    date_pattern = r"(\d{2})-(\d{2})-(\d{4})"
    j = 0
    merged_row = [
        [
            "Date",
            "Narration",
            "Chq/Ref No",
            "Withdrawal (Dr)/Deposit (Cr)",
            "Balance",
        ]
    ]

    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            if (
                df.loc[j, 0] != ""
                and df.loc[j, 1] != ""
                and df.loc[j, 2] == ""
                and df.loc[j + 1, 2] != ""
            ):
                # original_string = "This is a sample string with spaces"
                last_space_index = df.loc[j, 1].rfind(
                    " "
                )  # Find the index of the last space

                if last_space_index != -1:
                    str1 = df.loc[j, 1][
                        :last_space_index
                    ]  # Extract the substring after the last space
                    str2 = df.loc[j, 1][
                        last_space_index + 1 :
                    ]  # Extract the substring after the last space
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if next_date_match or df.loc[k, 0] != "" or df.loc[k, 4] != "":
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    if extracting_utility.get_duplicate_remove():
        df = df_total.drop_duplicates().reset_index(drop=True)
    df = df.applymap(extracting_utility.remove_trailing_newline)
    df = df.iloc[:, :5]
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 21_kotak_3. JUNE 2021.pdf
# pattern: "Chq / Ref number Dr / Cr Amount Description Balance Dr / Cr Date Sl. No."
def Pattern13(pdf_file, csv_output):
    pattern_text = (
        "Chq / Ref number Dr / Cr Amount Description Balance Dr / Cr Date Sl. No."
    )
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return
    # print("Pattern13")

    Bank_Name = "Kotak Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    cols = ["68,216,355,501,603,689,781,836"]
    cols *= 128
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", column=cols)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    # print(tables.n)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("test_temp.csv", mode="a", index=False, header=False)
        # camelot.plot(tables[0], kind='contour')
        # camelot.plot(tables[i], kind='grid')
        # plt.show(block = True)
        # continue
        # date_pattern = r"\d{2}-d{2}-\d{4}"
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        j = 0

        if len(df.columns) < 8:
            continue
        merged_row = []
        # merged_row = [["Date","Narration","Chq/Ref No","Withdrawal (Dr)/Deposit (Cr)","Balance"]]
        # merged_row = [["Sl.,No.","Date","Description","Chq / Ref number","Amount","Dr / Cr","Balance","Dr / Cr"]]
        while j < (len(df)):
            if "Opening balance" in df.loc[j, 0]:
                break
            # date_match = re.search(date_pattern,df.loc[j, 0])
            # print(df.loc[j])
            if len(df.loc[j]) == 9 and ("DR" in df.loc[j, 8] or "CR" in df.loc[j, 8]):
                k = j + 1
                new_row = df.loc[j]
                # print("k")
                # print(k)
                while k < (len(df)) and (
                    "DR" not in df.loc[k, 8] and "CR" not in df.loc[k, 8]
                ):
                    if "Opening balance" in df.loc[k, 0]:
                        break
                    new_row += df.loc[k]
                    j += 1
                    k += 1
                merged_row.append(new_row)
            elif len(df.loc[j]) == 8 and ("DR" in df.loc[j, 7] or "CR" in df.loc[j, 7]):
                k = j + 1
                new_row = df.loc[j]
                # print("k")
                # print(k)
                while k < (len(df)) and (
                    "DR" not in df.loc[k, 7] and "CR" not in df.loc[k, 7]
                ):
                    if "Opening balance" in df.loc[k, 0]:
                        break
                    new_row += df.loc[k]
                    j += 1
                    k += 1
                merged_row.append(new_row)
            else:
                j += 1

        df = pd.DataFrame(merged_row)
        # df.to_csv("test_temp.csv", mode="a", index=False, header=False)
        if len(df.columns) == 8:
            date_pattern = r"\d{2}/\d{2}/\d{4}"
            df = df.reset_index(drop=True)
            l = 0
            while l < (len(df)):
                # print(df.loc[j])
                # if "Opening balance" in df.loc[l,0]:
                #     break
                if df.loc[l, 1] == "":
                    # print(df.loc[j])
                    date_matches = re.search(date_pattern, df.loc[l, 0])
                    # print(date_matches.group())
                    df.loc[l, 1] = date_matches.group()
                    df.loc[l, 0] = df.loc[l, 0][: date_matches.start()]
                l += 1
        if len(df.columns) == 9:
            df = df.drop(2, axis=1)
            df = df.rename(columns={3: 2, 4: 3, 5: 4, 6: 5, 7: 6, 8: 7})
        if column_name_appened is False:
            column_name_appened = True
            df.loc[-1] = [
                "Sl.No.",
                "Date",
                "Description",
                "Chq / Ref number",
                "Amount",
                "Dr / Cr",
                "Balance",
                "Dr / Cr",
            ]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    if extracting_utility.get_duplicate_remove():
        df_total = df_total.drop_duplicates().reset_index(drop=True)
    df_total.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return
