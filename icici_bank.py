import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False


def initialize(pdf_file, csv_output):
    patterns = [
        Pattern22,
        Default,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break


# Done
# 7_ICICI_detailStatement_19-5-2021@11-44-35.pdf
# FASHION.FORWARD.01.01.2023.TO.28.02.2023
# pattern: "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
def Pattern22(pdf_file, csv_output):
    pattern_text = "Sr No Value Date Transactio\nn DateCheque\nNumberTransactio\nn RemarksDebit\nAmountCredit\nAmountBalance(IN\nR)"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )

    date_pattern = r"\d{2}-[A-Za-z]{3}-\n\d{4}"
    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # Remove trailing backslashes from all cells
        df = df.applymap(lambda x: x.rstrip("\/"))
        j = 0
        merged_row = []
        if i == 0:
            merged_row = [
                [
                    "Sr No",
                    "Value Date",
                    "Transaction Date",
                    "Cheque Number",
                    "Transaction Remarks",
                    "Debit Amount",
                    "Credit Amount",
                    "Balance(INR)",
                ]
            ]

        while j < (len(df)):
            date_match = re.search(date_pattern, df.loc[j, 1])
            if date_match:
                if "EP\n" in df.loc[j, 4]:
                    df.loc[j, 4] = df.loc[j, 4].replace("EP\n", "")
                merged_row.append(df.loc[j])
            j += 1
        df = pd.DataFrame(merged_row)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)

    df = df_total.drop_duplicates().reset_index(drop=True)
    df.to_csv(csv_output, mode="a", index=False, header=False)

    global Success
    Success = True
    return


def Default(pdf_file, csv_output):
    Bank_Name = "ICICI Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name,
        Bank_Name,
        extracting_utility.get_page_num(pdf_file),
    )

    tables = camelot.read_pdf(pdf_file, flavor="lattice", pages="all")
    df_total = pd.DataFrame()
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # Remove trailing backslashes from all cells
        df = df.applymap(lambda x: x.rstrip("\/"))
        df.to_csv(csv_output, mode="a", index=False, header=False)
    return
