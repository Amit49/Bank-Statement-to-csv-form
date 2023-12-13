import inspect
import pandas as pd
from tqdm import tqdm
import extracting_utility
import camelot
import re

Success = False

def initialize(pdf_file, csv_output):
    patterns = [
        PatternSaraswat1,
        # PatternSaraswat2,
    ]
    for pattern in patterns:
        pattern(pdf_file, csv_output)
        if Success:
            break

# Done
# 7294079_removed_1701754714.pdf
# pattern: "Date Particulars Instruments Dr Amount Cr Amount Total Amount"
def PatternSaraswat1(pdf_file, csv_output):
    pattern_text = "Date Particulars Instruments Dr Amount Cr Amount Total Amount"
    if not extracting_utility.search_keyword_in_pdf(pdf_file, pattern_text):
        return

    Bank_Name = "Saraswat Bank"
    extracting_utility.print_info(
        inspect.currentframe().f_code.co_name, Bank_Name, extracting_utility.Page_Num
    )
    cols = ["80,215,310,400,480"]
    cols *= 128
    TA = ["0,800,580,0"]
    TA *= 128
    tables = camelot.read_pdf(
        pdf_file, flavor="stream", pages="all",
        columns=cols,
        table_areas=TA,
    )
    df_total = pd.DataFrame()
    # def g(df):
    #     return df.loc[:,(df!="").any()]
    for i in tqdm(range(tables.n)):
        df = tables[i].df
        # df = g(df)
        # df.columns = range(len(df.columns))
        # extracting_utility.show_plot_graph(tables[i])
        df = extracting_utility.filter_dataframe(df,5,"Dr/Cr",1)
        df = extracting_utility.filter_dataframe(df,5,"PAGE",2)
        df_total = pd.concat([df_total, df], axis=0).reset_index(drop=True)
    df = df_total
    
    
    # df.loc[-1] = [
    #     "Date",
    #     "Particulars",
    #     "Instruments",
    #     "Dr Amount",
    #     "Cr Amount",
    #     "Total Amount\nDr/Cr",
    # ]
    # df.index = df.index + 1  # shifting index
    # df.sort_index(inplace=True)
    
    date_pattern = r"\d{2}-\d{2}-\d{4}"
    
    merged_row = [
        [
        "Date",
        "Particulars",
        "Instruments",
        "Dr Amount",
        "Cr Amount",
        "Total Amount\nDr/Cr",
        ]
    ]
    
    j = 0
    while j < (len(df)):
        date_match = re.search(date_pattern, df.loc[j, 0])
        if date_match:
            k = j + 1
            new_row = df.loc[j]
            while k < (len(df)):
                next_date_match = re.search(date_pattern, df.loc[k, 0])
                if (
                    next_date_match
                    or df.loc[k,5] != ""
                ):
                    break
                new_row += "\n" + df.loc[k]
                j += 1
                k += 1
            merged_row.append(new_row)
        j += 1
    df = pd.DataFrame(merged_row)
    
    # print(df.to_markdown(tablefmt="grid"))
    df.to_csv(csv_output, mode="w", index=False, header=False)
    global Success
    Success = True
    return