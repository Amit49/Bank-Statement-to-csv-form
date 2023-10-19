import PyPDF2
import camelot
import matplotlib.pyplot as plt

Page_Num = ""
remove_duplicate = False
def text_in_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        global Page_Num
        Page_Num = pdf_reader.numPages
        for page in range(Page_Num):
            page_content = pdf_reader.getPage(page)
            text += page_content.extractText()
    return text


def search_keyword_in_pdf(pdf_path, keyword):
    with open(pdf_path, "rb") as file:
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
def get_page_num(pdf_path):
    pdf_reader = PyPDF2.PdfFileReader(open(pdf_path, "rb"))
    global Page_Num
    Page_Num = pdf_reader.numPages
    return Page_Num

def print_info(Func_Name, Bank_Name, Page_Num):
    # data_list = [sys.argv[1],Func_Name]
    # # Specify the name of the CSV file you want to write to
    # csv_filename = "example.csv"

    # # Open the CSV file in write mode
    # with open(csv_filename, mode='a', newline='') as file:
    #     # Create a CSV writer object
    #     writer = csv.writer(file)
    
    #     # Write the list as a row in the CSV file
    #     writer.writerow(data_list)
    print("Function Name: ", Func_Name)
    print("Bank Name: ", Bank_Name)
    print("Page Num: ", Page_Num)
    
# Function to remove trailing newlines
def remove_trailing_newline(cell_value):
    if cell_value is not None and cell_value is str:
        return cell_value.rstrip("\n")
    return cell_value

def show_plot_graph(table):
    # camelot.plot(table, kind='grid')
    # camelot.plot(table, kind='joint')
    # camelot.plot(table, kind='textedge')
    camelot.plot(table, kind='contour')
    plt.show(block=True)

def set_duplicate_remove(should_remove):
    global remove_duplicate
    remove_duplicate = should_remove

def get_duplicate_remove():
    return remove_duplicate
