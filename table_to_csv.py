# import camelot
# import pandas as pd


# tables = camelot.read_pdf('HORIZON HIGH ~ HDFC ok.pdf',pages='all')
# print(tables)
# for i in range(tables.n):
#     tables[i].to_csv('foo1.csv',mode='a')

import sys
import tabula
import camelot
import pandas as pd
import PyPDF2

def extract_tables_with_tabula(pdf_file, csv_output):
    # tables = tabula.read_pdf(pdf_file, pages="all")
    # combined_table = pd.concat(tables)
    # combined_table.to_csv(csv_output, index=False)
    tabula.convert_into(pdf_file,csv_output,output_format="csv",pages="all")

def extract_tables_with_camelot(pdf_file, csv_output):
    tables = camelot.read_pdf(pdf_file,process_background=True, pages="all")
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


def main():
    if len(sys.argv) != 3:
        print("Usage: python script.py <pdf_file> <csv_output>")
        return

    pdf_file = sys.argv[1]
    csv_output = sys.argv[2]

    # with open(pdf_file, 'rb') as file:
        # pdf_content = file.read()
        # print(pdf_content)

    # if search_keyword_in_pdf(pdf_file,"HDFC"):
    #     print("HDFC")
    #     extract_tables_with_tabula(pdf_file, csv_output)
    # else:
    extract_tables_with_camelot(pdf_file, csv_output)

    print("Tables extracted and saved to", csv_output)


if __name__ == "__main__":
    main()
