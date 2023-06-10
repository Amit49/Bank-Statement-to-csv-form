import sys
import tabula
import camelot
import pandas as pd
import PyPDF2
import re
import matplotlib.pyplot as plt

# pdf_file =""
# csv_output=""
Success = False
def extract_tables_with_tabula(pdf_file, csv_output):
    # tables = tabula.read_pdf(pdf_file, pages="all")
    # combined_table = pd.concat(tables)
    # combined_table.to_csv(csv_output, index=False)
    tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")
    

def extract_tables_with_camelot(pdf_file, csv_output):
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all", row_tol=12)
    # combined_table = pd.concat([table.df for table in tables])
    # combined_table.to_csv(csv_output, index=False)
    for i in range(tables.n):
        # camelot.plot(tables[i], kind='joint').show()
        tables[i].to_csv(csv_output ,mode='a')
        
def search_keyword_in_pdf(pdf_path, keyword):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages

        for page_num in range(num_pages):
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

def Default(pdf_file, csv_output):

    # pattern_text ="Tran Date Chq No Particulars Debit Credit Balance Init."
    # if not search_keyword_in_pdf(pdf_file,pattern_text):
    #     return
    print("Default")
    
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1")
    for i in range(tables.n):
        df = tables[i].df
        df.to_csv(csv_output ,mode='a',index=False,header=False)
    return

# Done
# 1_Baroda_1. 01.04.2021 TO 31.05.2021 OK.pdf
# pattern: S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate

def Pattern1(pdf_file, csv_output):

    pattern_text ="S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return

    print("Pattern1")

    # extract_tables_with_camelot(pdf_file,csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all", row_tol=12)
    for i in range(tables.n):
        drop_column = []
        df = tables[i].df
        # print(df.columns)
        if(i!=0):
            df = df.drop(0)
        # print(df)
        # print("___________")
        # if i>1:
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
# pattern: "Tran Date Chq No Particulars Debit Credit Balance Init."

def Pattern2(pdf_file, csv_output):

    pattern_text ="Tran Date Chq No Particulars Debit Credit Balance Init"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern2")
    
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    # tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="1")
    for i in range(tables.n):
        df = tables[i].df
        if i==0:
            print("deleted")
            df.drop(0,inplace=True)
            new_row = pd.DataFrame([["Tran Date", "Chq No", "Particulars", "Debit", "Credit", "Balance", "Init. br"]])
            df = pd.concat([new_row, df], ignore_index=True)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        # tables[i].to_csv(csv_output ,mode='a')
        global Success
        Success = True
    return

# Done
# 5_ICICI BANK - SAVING ACCOUNT.pdf
# pattern: "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount"
def Pattern3(pdf_file, csv_output):

    pattern_text = "S No. Value Date Transaction Date Cheque Number Transaction Remarks Withdrawal Amount"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern3")
    
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=15)
    for i in range(tables.n):
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
# pattern: "Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance"
def Pattern4(pdf_file, csv_output):

    pattern_text ="Txn\nDateValue\nDateDescription Ref\nNo./Cheque\nNo.Branch\nCodeDebit Credit Balance" 
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return

    print("Pattern4")

    # extract_tables_with_camelot(pdf_file,csv_output)
    tables = camelot.read_pdf(pdf_file,flavor="lattice", pages="all")
    for i in range(tables.n):
        df = tables[i].df
        if(i!=0):
            df = df.drop(0)            
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

# Ongoing
# 
# pattern: "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
def Pattern5(pdf_file, csv_output):

    pattern_text = "Date\nParticulars\nChq. no\nWithdrawals\nDeposits\nBalance"
    if not search_keyword_in_pdf(pdf_file,pattern_text):
        return
    print("Pattern5")
    
    tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=12,col_tol=1)
    for i in range(tables.n):
        # if (i==(tables.n-2)):
        #     camelot.plot(tables[i], kind='text')
        #     plt.show(block=True)
        df = tables[i].df
        date_pattern = r'(\d{2})/(\d{2})/(\d{4})'
        for index, row in df.iterrows():
            print(row)
            if not re.search(date_pattern,row[0]):
                df = df.drop(index)
        df.to_csv(csv_output ,mode='a',index=False,header=False)
        global Success
        Success = True
    return

def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <pdf_file> <csv_output>")
        return

    pdf_file = sys.argv[1]
    csv_output = sys.argv[2]
     
    Pattern1(pdf_file, csv_output)
    Pattern2(pdf_file, csv_output)
    Pattern3(pdf_file, csv_output)
    Pattern4(pdf_file, csv_output)
    Pattern5(pdf_file, csv_output)

    if Success == False:
        Default(pdf_file, csv_output)

    print("Tables extracted and saved to", csv_output)


if __name__ == "__main__":
    main()

 # with open(pdf_file, 'rb') as file:
        # pdf_content = file.read()
        # print(pdf_content)

    # if search_keyword_in_pdf(pdf_file,"HDFC"):
    #     print("HDFC")
    #     extract_tables_with_tabula(pdf_file, csv_output)
    # else:
    
    
    # extract_tables_with_camelot(pdf_file, csv_output)