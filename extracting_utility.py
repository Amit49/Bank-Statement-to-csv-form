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


def remove_trailing_newline(cell_value):
    """
    Function to remove trailing newlines
    """
    if cell_value is not None and cell_value is str:
        return cell_value.rstrip("\n")
    return cell_value


def show_plot_graph(table, plot_type="textedge"):
  """
  Creates and shows a plot of the Camelot extracted table.

  Args:
    table: The Camelot extracted table object.
    plot_type: (Optional) The type of plot to generate.
      Supported types are "grid", "joint", "textedge", "contour", and "line".
      Defaults to "grid".
  """
  if plot_type not in ("grid", "joint", "textedge", "contour", "line"):
    raise ValueError(f"Invalid plot_type: {plot_type}")

  if plot_type == "grid":
    camelot.plot(table, kind="grid")
  elif plot_type == "joint":
    camelot.plot(table, kind="joint")
  elif plot_type == "textedge":
    camelot.plot(table, kind="textedge")
  elif plot_type == "contour":
    camelot.plot(table, kind="contour")
  elif plot_type == "line":
    camelot.plot(table, kind="line")

  plt.show(block=True)


def set_duplicate_remove(should_remove):
    global remove_duplicate
    remove_duplicate = should_remove


def get_duplicate_remove():
    return remove_duplicate


def filter_dataframe(df, column_name, string, condition_type, inclusive=False):
    """
    Filter a DataFrame based on a specified condition.

    Parameters:
    - df: DataFrame
        The input DataFrame.
    - column_name: str
        The name of the column to check for the specified string.
    - string: str
        The string to check for in the specified column.
    - condition_type: int
        1 for discarding rows before the string, 2 for discarding rows after the string.
    - inclusive: bool
        Whether to include or exclude the row.

    Returns:
    - DataFrame
        The filtered DataFrame.
    """
    # if condition_type not in [1, 2]:
    #     raise ValueError("Invalid condition_type. Use 1 for discarding rows before the string, 2 for discarding rows after the string.")
    if column_name not in df.columns:
        return df
    if inclusive:
        correction = 0
    else:
        correction = 1
    # Find the index of the specified string in the specified column
    index_of_string = df[
        df[column_name].str.contains(string, case=False, na=False)
    ].index
    if index_of_string.empty:
        return df
    if condition_type == 1:
        # Discard rows before the specified index
        filtered_df = df.loc[index_of_string[0] + correction :]
    elif condition_type == 2:
        # Discard rows after the specified index
        filtered_df = df.loc[: index_of_string[0] - correction]

    return filtered_df.reset_index(drop=True)

def print_markdown(df):
    print(df.to_markdown(tablefmt="grid"))
