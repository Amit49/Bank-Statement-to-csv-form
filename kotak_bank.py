import inspect
import os
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import tabula
import re

Success = False
Bank_Name = "Kotak Bank"

def initialize(pdf_file, csv_output):
    patterns = [
        Pattern10,
        Pattern11,
        Pattern12,
        Pattern13,
        PatternKotak5,
        PatternKotak6,
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
    pattern_text1 = "Chq/Ref No. Withdrawal (Dr) Date Narration Deposit (Cr) Balance"
    # pattern_text_1 = "Date Narration Chq/Ref. No Withdrawal (Dr) Deposit (Cr) Balance"
    if (
        not re.search(pattern_text, extracting_utility.text_in_pdf(pdf_file))
        and
        not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text1)
    ):
        return
    # print("Pattern10")

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
    date_pattern_2 = r"\d{2}-[A-Za-z]{3}-\d{2}"

    cols = ["89,275,350,430,527"]
    cols *= 128
    TA = ['0,785,601,0']
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols,
        table_ares=TA,
        edge_tol=500,
        split_text=True
    )
    # cols = ["89,275,350,430,527"]
    # cols *= 128
    # TA = [0,625,0,410]
    # # TA *= 128
    # tables = camelot.read_pdf(
    #     pdf_file,
    #     flavor="lattice",
    #     pages="all",
    #     # columns=cols,
    #     # table_ares=TA
    # )
    # tabula.convert_into(pdf_file, "temp.csv", output_format="csv", pages="all")
    
        
    # print(df_total1)
    # tables.export('foo.csv', f='csv')
    
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    if(len(df) == 0):
        df1 = tabula.read_pdf(pdf_file, pages="all")
        df_total1 = pd.DataFrame()
        for i in df1:
            df_total1 = pd.concat([df_total1, i], axis=0).reset_index(drop=True)
        df = df_total1
        df.fillna("", inplace=True)
        len_df = len(df.columns)
        new_column_names = []
        for i in range(len_df):
            new_column_names.append(i)
        df = df.set_axis(new_column_names, axis=1)
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
    df = df.applymap(extracting_utility.remove_trailing_newline)
    if extracting_utility.get_duplicate_remove():
        df = df.drop_duplicates().reset_index(drop=True)
    df = df.iloc[:, :6]
    df.to_csv(csv_output, mode="w", index=False, header=False)
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
    df_total.to_csv(csv_output, mode="w", index=False, header=False)
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

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    pages = int(extracting_utility.Page_Num-1)
    cols = ["85,270,350,475"]
    cols *= 128
    TA = ['0,632,585,0']
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file,
        flavor="stream",
        pages=f"1-{pages}",
        # edge_tol=500,
        column=cols,
        table_areas=TA,
        # row_tol = 1,
        # split_text=True,
    )
    tables_last_page = camelot.read_pdf(
        pdf_file,
        flavor="stream",
        pages=f"{pages+1}",
        column=cols,
    )
    # tables.export('foo.csv', f='csv')
    # tables_last_page.export('foo.csv', f='csv')
    column_name_appened = False
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    for i in tqdm(range(tables_last_page.n)):
        df = tables_last_page[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    df.fillna("", inplace=True)
    # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
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
            '''
            The following condition is applied when
            only 4 columns are found instead of 5 columns
            and column 2 and column 3 are merged togather.
            (found in "5.3.2023.to.6.10.2023.PDF")
            '''
            if df.loc[j,4]=="":
                df.loc[j,4] = df.loc[j,3]
                df.loc[j,3] = df.loc[j,2]
                df.loc[j,2] = ""
                '''
                The following condition is applied when
                column 1 and column 2 are merged togather
                and also
                column 3,4,5 shifted left
                (found in "BRIJESH.BAVISHI_19-20.pdf")
                '''
                if len(df.loc[j,0]) > 12:
                    if j+2 < len(df):
                        next_date_match = re.search(date_pattern, df.loc[j+1, 0])
                        next_next_date_match = re.search(date_pattern, df.loc[j+2, 0])
                        if not next_date_match and (next_next_date_match or "Statement  Summary" in df.loc[j+2,0]):
                            df.loc[j] = df.loc[j] + df.loc[j+1]
                            df.loc[j+1,0] = ""
                            df.loc[j+1,1] = ""
                            df.loc[j+1,2] = ""
                    parts = df.loc[j,0].split("\n",1)
                    if(len(parts) > 1):
                        df.loc[j,0] = parts[0]
                        df.loc[j,1] = parts[1]+" "+df.loc[j,1]

                parts = df.loc[j,1].split("\n")
                if(len(parts) > 1):
                    df.loc[j,1] = parts[0]
                    df.loc[j,2] = parts[1]

                if "UPI-" in df.loc[j,1] and df.loc[j,2] == "":
                    parts = df.loc[j,1].rsplit("UPI-",1)
                    df.loc[j,1] = parts[0]
                    df.loc[j,2] = "UPI-"+parts[1]
                if "UPI-" in df.loc[j,2] and j+1 < len(df) and df.loc[j+1,2]=="":
                    parts = df.loc[j+1,1].split("\n")
                    if(len(parts) > 1):
                        df.loc[j+1,1] = parts[0]
                        df.loc[j+1,2] = parts[1]
                    elif (len(parts) == 1):
                        df.loc[j+1,2] = df.loc[j+1,1]
                        df.loc[j+1,1] = ""
                if "CLG TO" in df.loc[j,1] and df.loc[j,2] == "":
                    parts = df.loc[j,1].rsplit(' ',1)
                    df.loc[j,1] = parts[0]
                    df.loc[j,2] = parts[1]
                if "FD PREMAT" in df.loc[j,1] and df.loc[j,2] == "":
                    parts = df.loc[j,1].rsplit(' ',1)
                    df.loc[j,1] = parts[0]
                    df.loc[j,2] = parts[1]
            '''
            The following condition is applied when
            column 1 and column 2 are merged togather
            (found in "BRIJESH.BAVISHI_19-20.pdf")
            '''
            if len(df.loc[j,0]) > 12:
                parts = df.loc[j,0].split("\n",1)
                if(len(parts) > 1):
                    df.loc[j,0] = parts[0]
                    df.loc[j,1] = parts[1]+" "+df.loc[j,1]

            '''
            The following condition is applied when
            column 2 and column 3 are merged togather.
            (found in "5.3.2023.to.6.10.2023.PDF")
            '''
            if (
                df.loc[j, 0] != ""
                and df.loc[j, 1] != ""
                and df.loc[j, 2] == ""
                and (j+1) < len(df)
                and df.loc[j + 1, 0] == ""
                and df.loc[j + 1, 2] != ""
            ):
                if df.loc[j, 1].endswith("UPI-"):
                    df.loc[j, 1] = df.loc[j, 1][:-4]
                    df.loc[j, 2] = "UPI-"+df.loc[j, 2]
                else:
                    last_space_index = df.loc[j, 1].rfind(" ")
                    if last_space_index != -1:
                        str1 = df.loc[j, 1][
                            :last_space_index
                        ]  # Extract the substring after the last space
                        str2 = df.loc[j, 1][
                            last_space_index + 1 :
                        ]  # Extract the substring after the last space
                        df.loc[j, 1] = str1
                        df.loc[j, 2] = str2
            '''
            The following condition is applied when
            column 4 and column 5 are merged togather
            in the 5th column.
            (found in "5.3.2023.to.6.10.2023.PDF")
            or
            column 4 and column 5 are shifted to right
            (found in "BRIJESH.BAVISHI_19-20.pdf")
            '''
            if "r)" not in df.loc[j, 3]:
                if "r)" in df.loc[j, 5]:
                    df.loc[j, 3] = df.loc[j, 4]
                    df.loc[j, 4] = df.loc[j, 5]
                    if j+1 < len(df):
                        next_date_match = re.search(date_pattern, df.loc[j+1, 0])
                        if not next_date_match:
                            if df.loc[j+1, 0]!= "" and df.loc[j+1, 1] == "":
                                df.loc[j+1, 1] = df.loc[j+1, 0]
                                df.loc[j+1, 0] = ""
                else:
                    parts = df.loc[j, 4].split("r)")
                    df.loc[j, 3] = parts[0] + "r)"
                    df.loc[j, 4] = parts[1] + "r)"
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if next_date_match:
                    break
                if (
                    df.loc[k, 0] != ""
                    or df.loc[k, 3] != ""
                    or df.loc[k, 4] != ""
                    or df.loc[k,1] == "Cust.Reln.No"
                    or df.loc[k, 1]=="Deposit (Cr)"
                    or df.loc[k, 1]=="Nominee Registered"
                    or df.loc[k, 1]=="Account No"
                    or df.loc[k, 1]=="Currency"
                    or df.loc[k, 1]=="Branch"
                    or df.loc[k, 2]=="Nominee Registered"
                    or df.loc[k, 2]=="Deposit (Cr)"
                ):
                    j += 1
                    k += 1
                    continue
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
    df.to_csv(csv_output, mode="w", index=False, header=False)
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

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    # print(csv_output)
    cols = ["68,216,355,501,603,689,781,836"]
    cols *= 128
    TA = ["0,825,840,0"]
    TA *= 128
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", column=cols,table_areas=TA)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    # print(tables.n)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
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
    df_total.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return


# Done
# 1.7.2023 to 31.7.2023.pdf
# pattern: "DATE TRANSACTION DETAILS CHEQUE/REFERENCE# DEBIT  CREDIT  BALANCE"
def PatternKotak5(pdf_file, csv_output):
    pattern_text = "DATE TRANSACTION DETAILS CHEQUE/REFERENCE# DEBIT  CREDIT  BALANCE"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["94,266,365,425,510"]
    cols *= 128
    TA = ["0,780,620,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols,
        table_areas=TA,
        split_text=True,
    )
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    
    date_pattern = r"\d{2} [A-Za-z]{3}, \d{4}"
    merged_row = [
        [
            "DATE",
            "TRANSACTION DETAILS",
            "CHEQUE/REFERENCE#",
            "DEBIT",
            "CREDIT",
            "BALANCE",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match and df.loc[j, 5]!= "":
            if len(df.loc[j, 0]) > 12:
                split_text = df.loc[j, 0].rsplit(maxsplit=1)
                # print(split_text)
                df.loc[j, 0] = split_text[0]
                if len(split_text) > 1:
                    df.loc[j, 1] = split_text[1]+df.loc[j, 1]
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if(not next_date_match and df.loc[k, 0] !=""):
                    df.loc[k, 1] = df.loc[k, 0]+df.loc[k,1]
                    df.loc[k, 0] = ""
                if (
                    next_date_match
                    or df.loc[k, 0] != ""
                    or df.loc[k, 1] == "SUMMARY"
                    or df.loc[k, 2] != ""
                    or df.loc[k, 3] != ""
                    or df.loc[k, 4] != ""
                    or df.loc[k, 5] != ""
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

# Done
# laxsh_3_1702358732.pdf
# pattern: "Date Narration Chq/Ref No Withdrawal (Dr) BalanceINR"
def PatternKotak6(pdf_file, csv_output):
    pattern_text = "Date Narration Chq/Ref No Withdrawal (Dr) BalanceINR"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["72,243,335,460,600"]
    cols *= 128
    TA = ["0,770,700,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols, table_areas=TA
    )
    # tables.export('foo.csv', f='csv')
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # extracting_utility.show_plot_graph(tables[i])
        df = extracting_utility.filter_dataframe(df,0,"Date",1)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    
    # date_pattern = r"\d{2}-\d{2}-\d{4}"
    date_pattern = r"\d{2}-\d{2}"

    merged_row = [
        [
            "Date",
            "Narration",
            "Chq/Ref No",
            "Withdrawal (Dr)",
            "Deposit(Cr)",
            "Balance",
        ]
    ]

    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match or df.loc[j,1] == "B/F":
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if (
                    next_date_match
                    or len(df.loc[k, 0]) > 4
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