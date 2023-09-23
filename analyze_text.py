import sys
import PyPDF2
def search_keyword_in_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        num_pages = pdf_reader.numPages

        for page_num in range(num_pages):
            page = pdf_reader.getPage(page_num)
            text = page.extractText()
            print(f"{page_num}::")
            print(text)
            # pattern1_text ="S.No Date Description Cheque\nNoDebit Credit Balance Value\nDate"
            # if pattern1_text in text:
            #     print(text)

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py <pdf_file>")
        return

    pdf_file = sys.argv[1]
    search_keyword_in_pdf(pdf_file)

if __name__ == "__main__":
    main()