import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False

def initialize(pdf_file, csv_output):
    patterns = [
            Pattern6,
        ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break

# Done
# 14_Akhand_Anand_1.4.2020 to 31.12.2020.pdf
# pattern: "Balance Credit Debit Chq No. Particulars Date"
def Pattern6(pdf_file, csv_output):
    pattern_text = "Balance Credit Debit Chq No. Particulars Date"
    pattern_text2 = "Akhand Anand"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text) or not extracting_utility.search_keyword_in_pdf(
        pdf_file, pattern_text2
    ):
        return

    Bank_Name = "Akhand Anand Bank"
    extracting_utility.print_info(inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num)
    # print(csv_output)
    # print("Pattern6")
    cols = ["65,250,324,409,494,585,655"]
    cols *= 128
    # tabula.convert_into(pdf_file, "temp.csv", output_format="csv", pages="all",stream="True")
    # tables = camelot.read_pdf(pdf_file,flavor="stream", pages="all",row_tol=12)
    tables = camelot.read_pdf(pdf_file, flavor="stream", pages="all", columns=cols)
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df.to_csv("csv_output.csv", mode="a", index=False, header=False)
        # camelot.plot(tables[i], kind='textedge')
        # plt.show(block=True)
        date_pattern = r"(\d{2})-(\d{2})-(\d{4})"
        merged_rows = []  # List to store the merged rows
        prev_row = None
        check = False
        for index, row in df.iterrows():
            if check:
                merged_rows.append(row)
                break
            if "Closing Balance" in row[1] and not check:
                merged_rows.append(row)
                check = True
                continue

            if row[0] == "" and "Balance" not in row[1]:
                if len(row[2]) > 6:
                    row[1] += row[2]
                    row[2] = ""
                # Merge with the previous row
                if prev_row is not None:
                    prev_row += "\n" + row
            else:
                # Add the row to the list of merged rows
                # print(len(row))
                if (
                    "Date" not in row[0]
                    and "Balance" not in row[1]
                    and not re.search(date_pattern, row[0])
                ):
                    continue
                if i != 0 and "Date" in row[0]:
                    continue
                merged_rows.append(row)
                prev_row = row
            # if i!=0 and "Date"  in row[0]:

        df = pd.DataFrame(merged_rows)
        substring_to_remove = "-------------------------------------------------------------------------------------"

        df = df.apply(lambda x: x.str.replace(substring_to_remove, ""))
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total.drop_duplicates().reset_index(drop=True)
    df = df.applymap(extracting_utility.remove_trailing_newline)
    if len(df.columns) > 7:
        df.drop(7, axis=1, inplace=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    global Success
    Success = True
    return