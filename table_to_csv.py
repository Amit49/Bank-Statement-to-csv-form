import os
import sys
import tabula
import camelot
import pandas as pd
import PyPDF2
import re
import math
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm

csv_output="output_file.csv"
Success = False
Bank_Name = ""
Page_Num = ""
def extract_tables_with_tabula(pdf_file, csv_output):
    # tables = tabula.read_pdf(pdf_file, pages="all")
    # combined_table = pd.concat(tables)
    # combined_table.to_csv(csv_output, index=False)
    tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    

def extract_tables_with_camelot(pdf_file, csv_output):
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all", row_tol=12)
    # combined_table = pd.concat([table.df for table in tables])
    # combined_table.to_csv(csv_output, index=False)
    for i in tqdm(range(tables.n)):
        # camelot.plot(tables[i], kind='joint').show()
        tables[i].to_csv(csv_output ,mode='a')

def text_in_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        global Page_Num
        Page_Num = pdf_reader.numPages
        for page in range(Page_Num):
            page_content = pdf_reader.getPage(page)
            text+= page_content.extractText()
    return text

def search_keyword_in_pdf(pdf_path, keyword):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        global Page_Num
        Page_Num = pdf_reader.numPages

        for page_num in range(Page_Num):
            page = pdf_reader.getPage(page_num)
            text = page.extractText()
            # print(text)
            if keyword in text:
                return True

    return False

# Done
# 3_Federal_1.10.2022 to 15.12.2022.pdf
# 4_Federal_Fi ok.pdf
# 6_ICICI ok.pdf
# 7_ICICI_detailStatement_19-5-2021@11-44-35.pdf
# 8_IDBI_2_2. 27.5.2021 TO 23.11.2021.pdf
# 9_MPassbook.pdf
# 11_stmt_58890100004756_1662869921041.pdf
# 12_The Sarvodaya Sahakari Bank Ltd_AccountStatement_ (1).pdf
# pattern: 

def Default(pdf_file, csv_file):

    # pattern_text ="Tran Date Chq No Particulars Debit Credit Balance Init."
    # if not search_keyword_in_pdf(pdf_file,pattern_text):
    #     return
    print("Default")
    
    # data_strings dictionary for bank name
    data_strings = {
        3: "Date Value Date ParticularsTran\nTypeCheque\nDetailsWithdrawals Deposits Balance",
        6: "Sl\nNoTran\nIdValue\nDateTransaction\nDateTransaction\nPosted DateCheque no /\nRef NoTransaction\nRemarksWithdra\nwal (Dr)Dep",
        7: "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance",
        8: "Txn Date Value DateCheque\nNoDescription CR/DRCC\nYSrl Balance (INR) Amount (INR)",
        9: "Transaction\nDateInstrument Id Narration Debit Credit Balance",
        11: "Transaction Details\nDate Description Amount Type",
        12: "Balance Credit Debit Chq No. Particulars Date Value Date"
    }
    
    bank_names_index={
        3: "Federal Bank",
        6: "ICICI Bank",
        7: "ICICI Bank",
        8: "IDBI Bank",
        9: "Bank of India",
        11: "Baroda Bank",
        12: "Sarvodaya Sahakari Bank"
    }
    index = 3
    for itr in data_strings:
        if search_keyword_in_pdf(pdf_file,data_strings[itr]):
            index = itr
            break
    
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = bank_names_index[index]
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # Remove trailing backslashes from all cells
        df = df.applymap(lambda x: x.rstrip('\/'))
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    return

# Done
# 1_Baroda_1. 01.04.2021 TO 31.05.2021 OK.pdf
# pattern: S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate

def Pattern1(pdf_file, csv_file):

    pattern_text ="S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Baroda Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # # print(csv_output)

    print("Pattern1")

    # extract_tables_with_camelot(pdf_file,csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all", row_tol=12)
    
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    isInserted = []
    for i in tqdm(range(tables.n)):
        drop_column = []
        df = tables[i].df
        j=0
        merged_row = []
        if i==0:
            merged_row = [["S.No","Date","Description","Cheque No","Debit","Credit","Balance","Value Date"]]
            
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j, 1])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                if df.loc[j,0]  in isInserted:
                    j+=1
                    continue
                isInserted.append(df.loc[j,0])
                merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        for column_index in range(4, len(df.columns)):
            for value in df.iloc[:, column_index]:
                if(value==""):
                    if column_index is not drop_column:
                        drop_column.append(column_index)
                    break
        # dropping empty extra column
        df.drop(drop_column,axis=1,inplace=True)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Done
# 2_axis_1. 01-04-2021 to 13-10-2021.pdf
# 2b_2. AXIS BANK.pdf
# pattern: "Tran Date Chq No Particulars Debit Credit Balance Init."

def Pattern2(pdf_file, csv_file):

    pattern_text ="Tran Date Chq No Particulars Debit Credit Balance Init"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Axis Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern2")
    column_name_appened = False
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all",line_scale=40)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        for index, row in df.iterrows():
                
                match = re.search(r'[a-zA-Z]', row[1])
                if match:
                    year = match.group(0)
                    updated_string = row[1][:match.start()]
                    remainder = row[1][match.start():]
                    row[1] = updated_string
                    row[2] = remainder + row[2]
        if column_name_appened is False:
            column_name_appened = True
            df = df.drop(0)
            df.loc[-1] = ["Tran Date", "Chq No", "Particulars", "Debit", "Credit", "Balance", "Init. br"]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True) 
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        # tables[i].to_csv(csv_output ,mode='a')
        global Success
        Success = True
    return

# Done
# 5_ICICI BANK - SAVING ACCOUNT.pdf
# pattern: "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount"
def Pattern3(pdf_file, csv_file):

    pattern_text = "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "ICICI Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern3")
    
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=15)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        if(i==0):
            df = df.drop(0)
        merged_rows = []  # List to store the merged rows
        prev_row = None
        for index, row in df.iterrows():
            if row[0] == '':
                # Merge with the previous row
                if prev_row is not None:
                    prev_row[4] += '\n' + row[4]
            else:
                # Add the row to the list of merged rows
                merged_rows.append(row)
                prev_row = row
        df = pd.DataFrame(merged_rows)

        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
        # tables[i].to_csv(csv_output ,mode='a')
    return

# Done
# 10_SBI_2. 1.6.2021 to 20.7.2021 OK.pdf
# 10_1_1. SBI.pdf
# pattern: "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
# pattern: "Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
def Pattern4(pdf_file, csv_file):

    
    pattern_text1 ="Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
    pattern_text2 ="Txn Date Value\nDateDescription Ref No./Cheque\nNo.Debit Credit Balance"
    if not search_keyword_in_pdf(pdf_file,pattern_text1) and not search_keyword_in_pdf(pdf_file,pattern_text2):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "SBI Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern4")
    global Success
    
    if search_keyword_in_pdf(pdf_file,pattern_text1):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all",joint_tol=20)
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            # camelot.plot(tables[i], kind='grid')
            # plt.show(block=True)
            df = df.drop(0)
            if(i==0):
                df.loc[-1] = ["Txn Date","Value Date","Description","Ref No./Cheque","No.Branch Code","Debit", "Credit", "Balance"]  # adding a row
                df.index = df.index + 1  # shifting index
                df.sort_index(inplace=True)     
            df.to_csv(csv_output ,mode='a',index=False,header=False)
            Success = True
    # 10_1_1. SBI.pdf
    if search_keyword_in_pdf(pdf_file,pattern_text2):
        # extract_tables_with_camelot(pdf_file,csv_output)
        tables = camelot.read_pdf(pdf_file,flavor="lattice",pages="all")
        for i in tqdm(range(tables.n)):
            df = tables[i].df
            if(i!=0):
                df = df.drop(0)

            # print("Pattern4222")
            for index, row in df.iterrows():
                
                match = re.search(r'\s\d{4}', row[1])
                if match:
                    year = match.group(0)
                    updated_string = row[1][:match.start()] + year
                    remainder = row[1][match.end():]
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
                    
                    match = re.search(r'\s\d{4}', row[2])
                    year = match.group(0)
                    updated_string = row[2][:match.end()]
                    remainder = row[2][match.end():]
                    row[1] = updated_string
                    row[2] = remainder
            df.to_csv(csv_output ,mode='a',index=False,header=False)
            Success = True
    return

def Pattern5_1(pdf_file, csv_file):
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "IDBI Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    cols = ['37,83,345,432,496,559']
    cols *= 128

    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    should_end = False
    date_pattern = r'(\d{2})-(\d{2})-(\d{4})'
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        # if (i==(tables.n-2)):
        # camelot.plot(tables[i], kind='grid')
        # plt.show(block=True)
        df = tables[i].df
        # df.to_csv("csv_output.csv" ,mode='a',index=False,header=False)
        if len(df.columns) > 2 and len(df.columns) < 6:
            df.insert(2, "Chq. no", "")
        
        merged_rows = []  # List to store the merged rows
        j=0
        while j<len(df):
            date_match = re.search(date_pattern,df.loc[j,0])
            if len(df.loc[j]) < 6:
                j+=1
                continue
            if  date_match:
                merged_rows.append(df.loc[j])
                j+=1
                continue
            elif df.loc[j,0] == "" and df.loc[j,3] == "" and df.loc[j,1] != "":
                merged_rows.append(df.loc[j])
                j+=1
                continue
            j+=1
        df = pd.DataFrame(merged_rows)
        df_total =  pd.concat([df_total, df], axis=0).reset_index(drop=True)
        
    j = 0
    merged_row = [["Date","Particulars","Chq. no","Withdrawals","Deposits","Balance"]]
    while j < (len(df_total)):
        date_match = re.search(date_pattern,df_total.loc[j,0])
        if date_match:
            k = j+1
            new_row = df_total.loc[j]
            if k<(len(df_total)):
                next_date_match = re.search(date_pattern,df_total.loc[k,0])
            while k<(len(df_total)) and  not next_date_match:
                new_row += '\n' + df_total.loc[k]
                j+=1
                k+=1
                if k<(len(df_total)):
                    next_date_match = re.search(date_pattern,df_total.loc[k,0])
            merged_row.append(new_row)
        j+=1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# 13_IDBI_2. 01.04.2021 to 13.10.2021.pdf
# pattern: "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
def Pattern5(pdf_file, csv_file):

    pattern_text = "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
    pattern_text1 = "Date Particulars Chq. no Withdrawals Deposits Balance"
    if not search_keyword_in_pdf(pdf_file,pattern_text) and not search_keyword_in_pdf(pdf_file,pattern_text1):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "IDBI Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern5")
    Pattern5_1(pdf_file, csv_output)
    return
    cols = ['37,83,345,432,496,559']
    cols *= 128

    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    should_end = False
    print(tables.n)
    for i in tqdm(range(tables.n)):
        # if (i==(tables.n-2)):
        # camelot.plot(tables[i], kind='grid')
        # plt.show(block=True)
        df = tables[i].df
        df.to_csv("csv_output.csv" ,mode='a',index=False,header=False)
        if len(df.columns) > 2 and len(df.columns) < 6:
            df.insert(2, "Chq. no", "")
        
        merged_rows = []  # List to store the merged rows
        prev_row = None
        for index, row in df.iterrows():
            
            if row.str.contains("Balance as on").any():
                should_end = True
                # print(row)
                # print(merged_rows)
                break
            # print(row)
            if len(row)>5 and row[0] == '' and row[2]==''and row[3]==''and row[4]=='':
                # Merge with the previous row
                if prev_row is not None:
                    prev_row += '\n' + row
            else:
                # Add the row to the list of merged rows
                merged_rows.append(row)
                prev_row = row
        
        df = pd.DataFrame(merged_rows)
        # Remove trailing newlines from all cells
        df = df.applymap(lambda x: x.rstrip('\n'))
        # print(dfx)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        # if(should_end):
        #     break
        global Success
        Success = True
    return

# Done
# 14_Akhand_Anand_1.4.2020 to 31.12.2020.pdf
# pattern: "Balance Credit Debit Chq No. Particulars Date"
def Pattern6(pdf_file, csv_file):


    pattern_text = "Balance Credit Debit Chq No. Particulars Date"
    pattern_text2 = "Akhand Anand"
    if not search_keyword_in_pdf(pdf_file,pattern_text) or not search_keyword_in_pdf(pdf_file,pattern_text2):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Akhand Anand Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern6")
    cols = ['65,250,324,409,494,585,655']
    cols *= 128
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=20,col_tol=20)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",columns=cols)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='textedge')
        # plt.show(block=True)
        date_pattern = r'(\d{2})-(\d{2})-(\d{4})'
        merged_rows = []  # List to store the merged rows
        prev_row = None
        check = False
        for index, row in df.iterrows():
            if check:
                merged_rows.append(row)
                break
            if "Closing" in row[1] and not check:
                merged_rows.append(row)
                check = True
                continue
            
            if row[0]=="" and "Balance"  not in row[1]:
                if(len(row[2])!=6 and len(row[2])!=0):
                    row[1]+=row[2]
                    row[2]=""
                # Merge with the previous row
                if prev_row is not None:
                    prev_row += '\n' + row
                
                    # print("row2")
                    # print("row2")
            else:
                # Add the row to the list of merged rows
                # print(len(row))
                if("Date" not in row[0] and "Balance"  not in row[1] and not re.search(date_pattern,row[0])):
                    continue
                if i!=0 and "Date" in row[0]:
                    continue
                merged_rows.append(row)
                prev_row = row
            # if i!=0 and "Date"  in row[0]:
                
        df = pd.DataFrame(merged_rows)
        substring_to_remove = '-------------------------------------------------------------------------------------'

        df = df.apply(lambda x: x.str.replace(substring_to_remove, ''))
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Done
# 15_INDUSLAND BANK_01.04.2021 TO 31.03.2022.pdf
# pattern: "Date\nParticulars\nChq./Ref. No\nWithDrawal\nDeposit\nBalance"
def Pattern7(pdf_file, csv_file):


    pattern_text = "Date\nParticulars\nChq./Ref. No\nWithDrawal\nDeposit\nBalance"
    pattern_text1 = "Date Particulars Chq./Ref.No. Withdrawl Deposit Balance"
    if not search_keyword_in_pdf(pdf_file,pattern_text) and not search_keyword_in_pdf(pdf_file,pattern_text1):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "INDUSLAND BANK"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern7")
    
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="1")
    # print(tables.n)
    cols = ['85,250,330,405,495,570']
    cols *= 128
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",columns=cols)
    last_df_row = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='textedge')
        # plt.show(block=True)
        merged_rows = []  # List to store the merged rows
        prev_row = None
        date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
        ignore = False
        for index, row in df.iterrows():
            date_match = re.search(date_pattern,row[0])
            if "For any queries of details" in row[1]:
                ignore = True
                continue
            if date_match:
                ignore = False
            if ignore:
                continue
            if row[0] == '':
                # Merge with the previous row
                if prev_row is not None:
                    prev_row[1] += '\n' + row[1]
            else:
                # Add the row to the list of merged rows
                merged_rows.append(row)
                prev_row = row

        df = pd.DataFrame(merged_rows)
        for index, row in df.iterrows():
            if "Date" not in row[0] and not re.search(date_pattern,row[0]):
                df = df.drop(index)
        j=0
        df = df.reset_index(drop=True)
        # print(df)
        while j< len(df):
            if not last_df_row.empty and df.loc[j,0]==(last_df_row[0]) and df.loc[j,2]==(last_df_row[2]) and df.loc[j,5]==(last_df_row[5]):
                df = df.drop([j]).reset_index(drop=True)
            if df.empty:
                break
            last_df_row = df.loc[j]
            j+=1
            # print(last_df_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return


def Pattern8_1(pdf_file, csv_file):
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "HDFC Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern8_1")
    cols = ['65,285,361,403,481,562,630']
    cols *= 128
    should_start_ignore = False
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",columns=cols)
    date_pattern = r"\d{2}/\d{2}/\d{2}"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("raw.csv" ,mode='a',index=False,header=False)
        j = 0
        merged_row = []
        if i==0:
            merged_row = []
        while j < (len(df)):
            if "Nomination : Registered" in df.loc[j,0]:
                j+=1
                continue
            stop_ignore = "From" not in df.loc[j,0]
            if should_start_ignore and stop_ignore :
                # print(cnt)
                # cnt+=1
                j+=1
                continue
            elif not stop_ignore:
                should_start_ignore =False
                j+=1
                continue
                
            if "HDFC BANK LIMITED" in  df.loc[j, 0]:
                should_start_ignore = True
                j+=1
                continue
            # print(df.loc[j])
            # print("*"*15)
            merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        df_total =  pd.concat([df_total, df], axis=0).reset_index(drop=True)
    # df_total.to_csv("csv_output.csv" ,mode='a',index=False,header=False)
    j = 0
    merged_row = [["Date","Narration","Chq./Ref.No.","Value Dt","Withdrawal Amt.","Deposit Amt.","Closing Balance"]]
    while j < (len(df_total)):
        date_match = re.search(date_pattern,df_total.loc[j,0])
        if date_match and df_total.loc[j,6] != "":
            k = j+1
            new_row = df_total.loc[j]
            if k<(len(df_total)):
                next_date_match = re.search(date_pattern,df_total.loc[k,0])
            while k<(len(df_total)) and  not next_date_match:
                if("This is a computer generated statement" in df_total.loc[k,5]):
                    break
                new_row += '\n' + df_total.loc[k]
                j+=1
                k+=1
                if k<(len(df_total)):
                    next_date_match = re.search(date_pattern,df_total.loc[k,0])
            merged_row.append(new_row)
        j+=1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

def Pattern8_2(pdf_file, csv_file):
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "HDFC Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    print("Pattern8_2")
    cols = ['65,285,361,403,481,562,630']
    cols *= 128
    should_start_ignore = False
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",columns=cols)
    date_pattern = r"\d{2}/\d{2}/\d{2}"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        j = 0
        merged_row = []
        if i==0:
            merged_row = []
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j,0])
            if date_match:
                if len(df.loc[j,0]) >8:
                    # print(df.loc[j])
                    df.loc[j,1] = df.loc[j,0][8:]+df.loc[j,1]
                    df.loc[j,0] = df.loc[j,0][0:8]
                    # print(df.loc[j])
                    # print("*"*20)
                merged_row.append(df.loc[j])
                j+=1
                continue
            elif df.loc[j,0] == "" and df.loc[j,2] == "" and df.loc[j,1] != "":
                merged_row.append(df.loc[j])
                j+=1
                continue
            j+=1
            
        df = pd.DataFrame(merged_row)
        df_total =  pd.concat([df_total, df], axis=0).reset_index(drop=True)
    # df_total.to_csv("csv_output2.csv" ,mode='a',index=False,header=False)
    j = 0
    merged_row = [["Date","Narration","Chq./Ref.No.","Value Dt","Withdrawal Amt.","Deposit Amt.","Closing Balance"]]
    while j < (len(df_total)):
        date_match = re.search(date_pattern,df_total.loc[j,0])
        if date_match and df_total.loc[j,6] != "":
            k = j+1
            new_row = df_total.loc[j]
            if k<(len(df_total)):
                next_date_match = re.search(date_pattern,df_total.loc[k,0])
            while k<(len(df_total)) and  not next_date_match:
                if("This is a computer generated statement" in df_total.loc[k,5]):
                    break
                new_row += '\n' + df_total.loc[k]
                j+=1
                k+=1
                if k<(len(df_total)):
                    next_date_match = re.search(date_pattern,df_total.loc[k,0])
            merged_row.append(new_row)
        j+=1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# HORIZON HIGH ~ HDFC ok.pdf
# pattern: "Date Narration Chq./Ref.No. Value Dt Withdrawal Amt. Deposit Amt. Closing Balance"
def Pattern8(pdf_file, csv_file):


    pattern_text = "Date Narration Chq./Ref.No. Value Dt Withdrawal Amt. Deposit Amt. Closing Balance"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "HDFC Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    Pattern8_2(pdf_file, csv_output)
    return
    Pattern8_1(pdf_file, csv_output)
    return
    print("Pattern8")
    cols = ['65,285,361,403,481,562,630']
    cols *= 128
    # dfs = tabula.read_pdf(pdf_file,pages="all",columns=cols)
    tabula.convert_into(pdf_file,"temp.csv",output_format="csv",pages="all")
    df = pd.read_csv('temp.csv',on_bad_lines='skip')
    os.remove('temp.csv')
    first_index = False
    prev = 0
    cur = 0
    date_pattern = r"\d{2}/\d{2}/\d{2}"
    merged_rows = []  # List to store the merged rows
    prev_row = None
    for index, row in df.iterrows():
        if("STATEMENT SUMMARY" in row[1]):
            break
        if(type(row[0]) is not str):
            row[0] = str(row[0])
        date_found = re.search(date_pattern,row[0])
        if "Date" in row[0] and "Narration" in row[1]:
            merged_rows.append(row)
            continue
            
        if row[0] != "nan" and not date_found:
            continue
        if date_found:
            if prev_row is not None:
                merged_rows.append(prev_row)
            prev_row = row
        elif row[0] == "nan" and prev_row is not None:
            if(type(row[1]) is not str):
                row[1] = str(row[1])
            if(type(prev_row[1]) is not str):
                prev_row[1] = str(prev_row[1])
            prev_row[1] += '\n'+ row[1]
    merged_rows.append(prev_row)
    df = pd.DataFrame(merged_rows)

    for index, row in df.iterrows():
        if  type(row[6]) is not str and math.isnan(row[6]):
            li = row[5].split(" ")
            row[6] = li.pop()
            if li:
                row[5] = li.pop()
            else:
                row[5] =""
            # print(li)
        if type(row[6]) == str:
            balance = float(row[6].replace(",",""))
        else:
            balance = row[6]
        if not first_index:
            prev = balance
            first_index=True
            continue
        cur = balance
        row[4] = str(row[4])
        if row[4]=="nan":
            row[4]=""
        row[5] = str(row[5])
        if row[5]=="nan":
            row[5]=""
        # print("/"*5)
        # print(f"{row[4]}\t {row[5]}\t {row[6]} '''''{prev}")                
        if cur > prev and row[5] == "":
            # print("/"*5)
            # print(f"{row[4]}\t {row[5]}\t {row[6]} '''''{prev}")
            row[5] = row[4]
            row[4] =""            
            # print(f"{row[4]}\t {row[5]}\t {row[6]}")
            # print("*"*5)
        elif cur < prev and row[4] == "":
            # print("="*5)
            # print(f"{row[4]}\t {row[5]}\t {row[6]} '''''{prev}")
            row[4] = row[5]
            row[5] =""            
            # print(f"{row[4]}\t {row[5]}\t {row[6]}")
            # print("."*5)
        # print(f"{row[4]}\t {row[5]}\t {row[6]}")
        # print("."*5)
        
        prev = cur
    df.loc[-1] = ["Date","Narration","Chq./Ref.No.","Value Dt","Withdrawal Amt.","Deposit Amt.","Closing Balance"]  # adding a row
    df.index = df.index + 1  # shifting index
    df.sort_index(inplace=True) 
    df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# 17_INDUSLAND FY 2021-22.pdf
# pattern: "Date Description Credit Type Debit\nBalance"
def Pattern9(pdf_file, csv_file):

    text = text_in_pdf(pdf_file)
    pattern_text = "Date Description Credit Type Debit\nBalance"
    if pattern_text not in text:
        return
    print("Pattern9")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "INDUSLAND BANK"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",column=cols)
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    def rows_list(ind):
        new_rows = []
        text = row[ind]
        split_text = text.split('\n')
        for split_value in split_text:
                new_rows.append( split_value )
        return new_rows
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='textedge')
        # camelot.plot(tables[i], kind='grid')
        # plt.show(block=True)
        new_rows_0 = []
        new_rows_1 = []
        new_rows_2 = []
        new_rows_3 = []
        new_rows_4 = []
        new_rows_5 = []
        start_index = 0
        
        for index, row in df.iterrows():
            if(row[0] == "Date"):
                continue
            new_rows_0 = rows_list (0)
            new_rows_1 = rows_list (1)
            # new_rows_2 = rows_list (2)
            new_rows_3 = rows_list (3)
            new_rows_4 = rows_list (4)
            new_rows_5 = rows_list (5)
            for j in range(len(new_rows_0)):
                date_match = re.search(new_rows_0[j], text)
                decimal_match = re.search(new_rows_3[j], text)

                # Extract the substrings if both patterns are found
                if date_match and decimal_match:
                    date_string = date_match.group()
                    decimal_string = decimal_match.group()
                    text1 = text[text.index(date_string) + len(date_string):text.index(decimal_string)]
                    text = text[text.index(decimal_string) + len(decimal_string)+5:]
                    new_rows_2.append( text1 )
            df = pd.DataFrame({'0':new_rows_0,
                               '1':new_rows_1,
                               '2':new_rows_2,
                               '3':new_rows_3,
                               '4':new_rows_4,
                               '5':new_rows_5,})
            # new_row = pd.DataFrame([["Date", "Type", "Description", "Debit", "Credit", "Balance"]])
            if i == 0:
                # print("????")
                df.loc[-1] = ["Date", "Type", "Description", "Debit", "Credit", "Balance"]
                df.index = df.index + 1  # shifting index
                df.sort_index(inplace=True) 
            df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# 18_kotak ok.pdf
# pattern: "Date Narration Chq/Ref No. Withdrawal (Dr) Deposit (Cr) Balance"
# pattern: "Date Narration Chq /Ref. No Withdrawal(Dr) Deposit(Cr) Balance"
def Pattern10(pdf_file, csv_file):

    pattern_text = r"Date.*Narration.*Chq.*Ref.*No.*Withdrawal.*(Dr).*Deposit.*(Cr).*Balance"
    # pattern_text_1 = "Date Narration Chq/Ref. No Withdrawal (Dr) Deposit (Cr) Balance"
    if not re.search(pattern_text,text_in_pdf(pdf_file)):
        return
    print("Pattern10")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Kotak Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
    date_pattern_2 = r"\d{2}-[A-Za-z]{3}-\d{2}"
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="1",col_tol=10)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    tabula.convert_into(pdf_file,"temp.csv",output_format="csv",pages="all")
    # Delimiter
    data_file_delimiter = ','

    # The max column count a line in the file could have
    largest_column_count = 0

    # Loop the data lines
    with open("temp.csv", 'r') as temp_f:
        # Read the lines
        lines = temp_f.readlines()

        for l in lines:
            # Count the column count for the current line
            column_count = len(l.split(data_file_delimiter)) + 1
            
            # Set the new most column count
            largest_column_count = column_count if largest_column_count < column_count else largest_column_count

    # Generate column names (will be 0, 1, 2, ..., largest_column_count - 1)
    column_names = [i for i in range(0, largest_column_count)]
    df = pd.read_csv('temp.csv',names=column_names)
    # print(df)
    os.remove('temp.csv')
    drop_row = []
    j=0
    merged_row = []
    merged_row = [["Date", "Narration", "Chq/Ref No.", "Withdrawal (Dr)", "Deposit (Cr)", "Balance"]]
    while j < (len(df)):
        if type(df.loc[j,0]) != str:
            j+=1
            continue
        date_match = re.search(date_pattern,df.loc[j,0])
        date_match_2 = re.search(date_pattern_2,df.loc[j,0])
        if date_match or date_match_2:
            merged_row.append(df.loc[j])
        j+=1
    df = pd.DataFrame(merged_row)
    df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# 19_kotak_01. 01.04.2022 TO 31.08.2022.pdf
# pattern: "# TRANSACTION TRANSACTION DETAILS CHQ / REF NO. DEBIT(₹) CREDIT(₹) BALANCE(₹)"
def Pattern11(pdf_file, csv_file):

    pattern_text = "# TRANSACTION TRANSACTION DETAILS CHQ / REF NO. DEBIT(₹) CREDIT(₹) BALANCE(₹)"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern11")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Kotak Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=15)
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2} [A-Za-z]{3} \d{4}"
        drop_row = []
        for index, row in df.iterrows():
            date_match = re.search(date_pattern,row[1])
            if not date_match:
                drop_row.append(index)
        # print(drop_row)
        df.drop(drop_row,inplace=True)
        # print(df.columns)
        if len(df.columns)>6 and column_name_appened is False:
            column_name_appened = True
            df.loc[-1] = ["#", "TRANSACTION",  "TRANSACTION DETAILS", "CHQ / REF NO.", "DEBIT", "CREDIT", "BALANCE"]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True) 
        
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Done
# 20_kotak_2_1. 01.04.2021 TO 26.08.2021.PDF
# pattern: "Date Narration Withdrawal (Dr)/\nDeposit (Cr)Balance Chq/Ref"
def Pattern12(pdf_file, csv_file):

    pattern_text = "Date Narration Withdrawal (Dr)/\nDeposit (Cr)Balance Chq/Ref"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern12")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Kotak Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    # print(tables.n)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r'(\d{2})-(\d{2})-(\d{4})'
        j=0
        merged_row = []
        if i==0:
            merged_row = [["Date","Narration","Chq/Ref No","Withdrawal (Dr)/Deposit (Cr)","Balance"]]
            
        while j < (len(df))-1:
            date_match = re.search(date_pattern,df.loc[j, 0])
            if date_match:
                # print(f"Row:::\n{df.loc[j+1]}")
                if df.loc[j+1, 0] == "" and (df.loc[j+1, 1] != "" or df.loc[j+1, 2] != ""):
                    new_row = df.loc[j] + df.loc[j+1]
                    # print(f"New Row:::\n{new_row}")
                    merged_row.append(new_row)
                    j+=2
                    continue
                else:
                    merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        # print(f"Merged Row:::\n{merged_row}")
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Done
# 21_kotak_3. JUNE 2021.pdf
# pattern: "Chq / Ref number Dr / Cr Amount Description Balance Dr / Cr Date Sl. No."
def Pattern13(pdf_file, csv_file):

    pattern_text = "Chq / Ref number Dr / Cr Amount Description Balance Dr / Cr Date Sl. No."
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern13")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Kotak Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1",process_background=True)
    # tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    column_name_appened = False
    # print(tables.n)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[0], kind='contour')
        # plt.show(block = True)
        # date_pattern = r"\d{2}-d{2}-\d{4}"
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        j=0
        
        if len(df.columns) < 8:
            continue
        merged_row = []
        # merged_row = [["Date","Narration","Chq/Ref No","Withdrawal (Dr)/Deposit (Cr)","Balance"]]
        # merged_row = [["Sl.,No.","Date","Description","Chq / Ref number","Amount","Dr / Cr","Balance","Dr / Cr"]]
        while j < (len(df)):
            if "Opening balance" in df.loc[j,0]:
                break
            # date_match = re.search(date_pattern,df.loc[j, 0])
            # print(df.loc[j])
            if len(df.loc[j])==9 and ("DR" in df.loc[j, 8] or "CR" in df.loc[j, 8]):
                k = j+1
                new_row = df.loc[j]
                # print("k")
                # print(k)
                while k<(len(df)) and ("DR" not in df.loc[k, 8] and "CR" not in df.loc[k, 8]):
                    if "Opening balance" in df.loc[k,0]:
                        break
                    new_row += df.loc[k]
                    j+=1
                    k+=1
                merged_row.append(new_row)
            elif len(df.loc[j])==8 and ("DR" in df.loc[j, 7] or "CR" in df.loc[j, 7]):
                
                k = j+1
                new_row = df.loc[j]
                # print("k")
                # print(k)
                while k<(len(df)) and ("DR" not in df.loc[k, 7] and "CR" not in df.loc[k, 7]):
                    if "Opening balance" in df.loc[k,0]:
                        break
                    new_row += df.loc[k]
                    j+=1
                    k+=1
                merged_row.append(new_row)
            else:
                j+=1

        df = pd.DataFrame(merged_row)
        df.to_csv("test_temp.csv" ,mode='a',index=False,header=False)
        if len(df.columns) == 8:
            date_pattern = r"\d{2}/\d{2}/\d{4}"
            df = df.reset_index(drop=True)
            # print(df)
            l=0
            while l < (len(df)):
                # print(df.loc[j])
                # if "Opening balance" in df.loc[l,0]:
                #     break
                if df.loc[l,1] == "":
                    # print(df.loc[j])
                    date_matches = re.search(date_pattern,df.loc[l, 0])
                    df.loc[l,1] = df.loc[l,0][date_matches.start():10]
                    df.loc[l,0] = df.loc[l,0][:date_matches.start()]
                l+=1
        if len(df.columns) == 9:
            df = df.drop(2,axis=1)
        if column_name_appened is False:
            column_name_appened = True
            df.loc[-1] = ["Sl.No.","Date","Description","Chq / Ref number","Amount","Dr / Cr","Balance","Dr / Cr"]
            df.index = df.index + 1  # shifting index
            df.sort_index(inplace=True) 
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Done
# 22_OpTransactionHistoryUX504-01-2023 (1).pdf
# pattern: "NARRATION DEPOSIT(CR) DATE CHQ.NO. WITHDRAWAL(DR) BALANCE(INR)"
def Pattern14(pdf_file, csv_file):

    pattern_text = "NARRATION DEPOSIT(CR) DATE CHQ.NO. WITHDRAWAL(DR) BALANCE(INR)"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern14")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Baroda Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=12)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        drop_row = []
        for index, row in df.iterrows():
            date_match = re.search(date_pattern,row[0])
            if "DATE" not in row[0] and (not date_match or "Page" in row[2]):
                drop_row.append(index)
        df = df.drop(drop_row).reset_index(drop=True) 
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True

# Done
# 23_paytm_1. 01.04.2021 TO 25.08.2021.pdf
# pattern: "DATE & TIME TRANSACTION DETAILS AMOUNT AVAILABLE BALANCE"
def Pattern15(pdf_file, csv_file):

    pattern_text = "DATE & TIME TRANSACTION DETAILS AMOUNT AVAILABLE BALANCE"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern15")

    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Paytm"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    date_pattern = r"\d{1} [A-Za-z]{3} \d{4}"
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        j=0
        merged_row = []
        if i==0:
            # merged_row = [["Date","Narration","Chq/Ref No","Withdrawal (Dr)/Deposit (Cr)","Balance"]]
            merged_row = [["DATE & TIME", "TRANSACTION DETAILS", "AMOUNT", "AVAILABLE BALANCE"]]
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j,0])
            is_balance_col_empty = False
            if date_match and df.loc[j,3] == "":
                # print("WHAT!!!")
                # print(df.loc[j,3])
                k = j+1
                new_row = df.loc[j-1]+df.loc[j]
                next_date_match = re.search(date_pattern,df.loc[k,0])
                # print("[[[[[[[[[]]]]]]]]]")
                # print(df.loc[k,0])
                # print(next_date_match)
                # print("((((((()))))))")
                while k<(len(df)) and  not next_date_match and df.loc[k,3] == "":
                    new_row += '\n' + df.loc[k]
                    j+=1
                    k+=1
                    if k<(len(df)):
                        next_date_match = re.search(date_pattern,df.loc[k,0])
                merged_row.append(new_row)
            # print("========")
            # print(df.loc[j,0])
            # print(date_match)
            # print("********")
            elif date_match:
                k = j+1
                new_row = df.loc[j]
                next_date_match = re.search(date_pattern,df.loc[k,0])
                # print("[[[[[[[[[]]]]]]]]]")
                # print(df.loc[k,0])
                # print(next_date_match)
                # print("((((((()))))))")
                while k<(len(df)) and  not next_date_match:
                    new_row += '\n' + df.loc[k]
                    j+=1
                    k+=1
                    if k<(len(df)):
                        next_date_match = re.search(date_pattern,df.loc[k,0])
                merged_row.append(new_row)
            # else:

            j+=1
        df = pd.DataFrame(merged_row)
        df = df.apply(lambda x: x.str.replace('₹', ''))
        # print(df)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    return

# Done
# 24_SURAT PEOPLE CO-PO BANK 1.4.21 TO 30.9.2021.pdf
# pattern: "Date Particulars Withdr awals Deposits Balance"
def Pattern16(pdf_file, csv_file):
    
    pattern_text = "Date Particulars Withdr awals Deposits Balance"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern16")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "SURAT PEOPLE CO-PO BANK"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=12)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}-[A-Za-z]{3}-\d{4}"
        j=0
        merged_row = []
        if i==0:
            merged_row = [["Date","Particulars","Withdrawal","Deposit","Balance"]]
            
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j, 0])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                # print(f"Row:::\n{df.loc[j]}")
                if j+1 < (len(df)) and df.loc[j+1, 0] == "" and df.loc[j+1, 1] != "" :
                    new_row = df.loc[j] + df.loc[j+1]
                    # print(f"New Row:::\n{new_row}")
                    merged_row.append(new_row)
                    j+=2
                    continue
                else:
                    merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    
# Done
# 25_Union_Bank_1.8.2021 TO 31.3.2022.pdf
# pattern: "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
def Pattern17(pdf_file, csv_file):
    
    pattern_text = "Tran Id Tran Date Remarks Amount (Rs.) Balance (Rs.)"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern17")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Union Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        date_pattern = r"\d{2}/\d{2}/\d{4}"
        j=0
        merged_row = []
        if i==0:
            merged_row = [["Tran Id","Tran Date","Remarks","Amount (Rs.)","Balance (Rs.)"]]
            
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j, 1])
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            if date_match:
                # print(f"Row:::\n{df.loc[j]}")
                if j+1 < (len(df)) and df.loc[j+1, 1] == "" and df.loc[j+1, 2] != "" :
                    new_row = df.loc[j] + df.loc[j+1]
                    # print(f"New Row:::\n{new_row}")
                    merged_row.append(new_row)
                    j+=2
                    continue
                else:
                    merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True
    
# Done
# 26_VARCHHA BANK_01.04.2021 TO 31.03.2022.pdf
# pattern: "TRN. Date | Value Date | Narration Chq/Ref.No Debit Credit} Closing Bal"
def Pattern18(pdf_file, csv_file):
    
    pattern_text = r"TRN.*Date.*Value Date.*Narration.*Chq/Ref\.No.*Debit.*Credit.*Closing Bal"
    if not re.search(pattern_text,text_in_pdf(pdf_file)):
        return
    print("Pattern18")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "VARCHHA BANK"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    cols = ['179,298,579,728,857,990,1130']
    cols *= 128
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # camelot.plot(tables[i], kind='textedge')
        # plt.show(block=True)
        date_pattern = r"\d{2}-\d{2}-\d{4}"
        pattern = r"\|"
        j=0
        merged_row = []
        if i==0:
            merged_row = [["TRN.  Date","Value  Date","Narration","Chq/Ref.No","Debit","Credit","Closing  Bal"]]
            
        while j < (len(df)):
            match_ = re.search(pattern,df.loc[j, 0])
            date_match = re.search(date_pattern,df.loc[j, 0])
            date_match_2 = re.search(date_pattern,df.loc[j, 1])
            
            # print(date_match)
            # print(df.loc[j, 0])
            # print("*"*6)
            
            if date_match:
                if match_:
                    str1 = df.loc[j, 0][:match_.start()]
                    str2 = df.loc[j, 0][match_.start()+1:]
                    df.loc[j, 0] = str1
                    df.loc[j, 1] = str2
                    # print(df.loc[j, 0])
                    # print("."*10)
                    # print(str1)
                    # print(","*10)
                    # print(str2)
                    # print("*"*10)
                elif len(df.loc[j, 1]) > 10:
                    str1 = df.loc[j, 1][:10]
                    str2 = df.loc[j, 1][10:] + df.loc[j, 2]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                    # print(df.loc[j, 1])
                    # print(len(df.loc[j, 1]))
                elif len(df.loc[j, 1]) < 1:
                    str1 = df.loc[j, 2][:10]
                    str2 = df.loc[j, 2][10:]
                    df.loc[j, 1] = str1
                    df.loc[j, 2] = str2
                merged_row.append(df.loc[j])
            j+=1
        # df = pd.DataFrame(merged_row)
        # df.drop(df.loc[0].index,inplace=True)
        # if i == 0:
        #     df.loc[-1] = ["TRN.  Date","Value  Date","Narration","Chq/Ref.No","Debit","Credit","Closing  Bal"]
        #     df.index = df.index + 1  # shifting index
        #     df.sort_index(inplace=True) 
        df = pd.DataFrame(merged_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True

# Done
# HIRVA 1.8 TO 6.8.pdf
# pattern: "TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
def Pattern19(pdf_file, csv_file):
    
    pattern_text ="TypeTran ID Cheque Details Withdrawals Deposits BalanceDr/\nCr"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern19")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Federal Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    skip_first = True
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all",line_scale=40)
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        for index, row in df.iterrows():
            if "Date" in row[0]:
                if skip_first:
                    skip_first = False
                else:
                    df.drop(index,inplace=True)
                    break
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True 
    return



# Done
# 27_BHUMI BOB 01.03.2023 TO 31.03.2023.pdf
# pattern: "Serial/\nNoTransaction/\nDateValue/\nDateDescription Cheque/\nNumberDebit Credit Balance"
def Pattern20(pdf_file, csv_file):
    
    pattern_text ="Serial\nNoTransaction\nDateValue\nDateDescription Cheque\nNumberDebit Credit Balance\n"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern20")
    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Baroda Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"
    # print(csv_output)
    skip_first = True
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=14)
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    #For avoiding duplicate
    isInserted = []
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("csv_output.csv" ,mode='a',index=False,header=False)
        j=0
        merged_row = []
        if i==0:
            merged_row = [["Serial No","Transaction Date","Value Date","Description", "Cheque Number","Debit", "Credit","Balance"]]
        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j,1])
            if date_match:
                if df.loc[j,0]  in isInserted:
                    j+=1
                    continue
                isInserted.append(df.loc[j,0])
                merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    global Success
    Success = True 
    return

# Done
# 1690969903.pdf
# pattern: "Transaction DetailsDateDescriptionAmountType"
def Pattern21(pdf_file, csv_file):

    pattern_text = "Transaction DetailsDateDescriptionAmountType"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern21")

    # Extract the file name from the full path
    file_name = os.path.basename(pdf_file)
    Bank_Name = "Baroda Bank"
    global csv_output
    csv_output = Bank_Name+"_"+str(Page_Num)+"_"+file_name[:-4]+".csv"

    date_pattern = r"\d{2}/\d{2}/\d{4}"
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        j=0
        merged_row = []
        if i==0:
            merged_row = [["Date","Description","Amount","Type"]]

        while j < (len(df)):
            date_match = re.search(date_pattern,df.loc[j, 0])
            if date_match:
                merged_row.append(df.loc[j])
            j+=1
        df = pd.DataFrame(merged_row)
        df.to_csv(csv_output ,mode='a',index=False,header=False)

    global Success
    Success = True
    return

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_file> <csv_output>")
        return

    pdf_file = sys.argv[1]
    global csv_output
    if len(sys.argv) == 3:
        csv_output = sys.argv[2]
     
    Pattern1(pdf_file, csv_output)
    if Success == False:
        Pattern2(pdf_file, csv_output)
    if Success == False:
        Pattern3(pdf_file, csv_output)
    if Success == False:
        Pattern4(pdf_file, csv_output)
    if Success == False:
        Pattern5(pdf_file, csv_output)
    if Success == False:
        Pattern6(pdf_file, csv_output)
    if Success == False:
        Pattern7(pdf_file, csv_output)
    if Success == False:
        Pattern8(pdf_file, csv_output)
    if Success == False:
        Pattern9(pdf_file, csv_output)
    if Success == False:
        Pattern10(pdf_file, csv_output)
    if Success == False:
        Pattern11(pdf_file, csv_output)
    if Success == False:
        Pattern12(pdf_file, csv_output)
    if Success == False:
        Pattern13(pdf_file, csv_output)
    if Success == False:
        Pattern14(pdf_file, csv_output)
    if Success == False:
        Pattern15(pdf_file, csv_output)
    if Success == False:
        Pattern16(pdf_file, csv_output)
    if Success == False:
        Pattern17(pdf_file, csv_output)
    if Success == False:
        Pattern18(pdf_file, csv_output)
    if Success == False:
        Pattern19(pdf_file, csv_output)
    if Success == False:
        Pattern20(pdf_file, csv_output)
    if Success == False:
        Pattern21(pdf_file, csv_output)
    if Success == False:
        Default(pdf_file, csv_output)

    print("Tables extracted and saved to", csv_output)


if __name__ == "__main__":
    main()
