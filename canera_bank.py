import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


def Default(pdf_file, csv_output):
    Bank_Name = "Canera Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name,
        Bank_Name,
        extracting_utility.get_page_num(pdf_file),
    )

    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    date_pattern = r"\d{2}-[A-Za-z]{3}-\d{2}"
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # Remove trailing backslashes from all cells
        df = df.applymap(lambda x: x.rstrip("\/"))
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    j = 0
    merged_row = [
                [
                    "TRANS DATE",
                    "Value  Date",
                    "Branch",
                    "REF/CHQ.NO",
                    "DESCRIPTION",
                    "WITHDRAWS",
                    "DEPOSIT",
                    "BALANCE",
                ]
            ]
    # print(df.to_string())
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if next_date_match:
                    break
                if df.loc[k,0]!="":
                    j += 1
                    k += 1
                    continue
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row).reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)
    return
