import sys
import akand_anand_bank
import axis_bank
import bank_of_baroda
import bank_of_india
import canera_bank
import federal_bank
import hdfc_bank
import icici_bank
import idbi_bank
import indusind_bank

csv_output = ""


def findPatternForBank():
    global csv_output

    pdf_file = sys.argv[1]
    csv_output = sys.argv[2]
    bank_num = int(sys.argv[3])
    if bank_num == 1:
        akand_anand_bank.initialize(pdf_file, csv_output)
    elif bank_num == 2:
        axis_bank.initialize(pdf_file, csv_output)
    elif bank_num == 3:
        bank_of_baroda.initialize(pdf_file, csv_output)
    elif bank_num == 4:
        bank_of_india.initialize(pdf_file, csv_output)
    elif bank_num == 5:
        canera_bank.initialize(pdf_file, csv_output)
    elif bank_num == 6:
        federal_bank.initialize(pdf_file, csv_output)
    elif bank_num == 7:
        hdfc_bank.initialize(pdf_file, csv_output)
    elif bank_num == 8:
        icici_bank.initialize(pdf_file, csv_output)
    elif bank_num == 9:
        idbi_bank.initialize(pdf_file, csv_output)
    elif bank_num == 10:
        indusind_bank.initialize(pdf_file, csv_output)
    else:
        print("Bank not found")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python bank_table_to_csv.py <pdf_file> <csv_output> <bank_number>"
        )
        return
    # Bank number map
    # 1 = AKHAND ANAND BANK
    # 2 = AXIS BANK
    # 3 = BANK OF BARODA
    # 4 = BANK OF INDIA
    # 5 = CANERA BANK
    # 6 = FEDRALBank
    # 7 = HDFC BANK
    # 8 = ICICI bank
    # 9 = IDBI bank
    # 10 = INDUSLAND bank
    # 11 = KOTAK bank
    # 12 = MEHASANA COP OP. BANK
    # 13 = PAYTM BANK
    # 14 = PUNJAB NATIONAL BANK
    # 15 = SARVODAY BANK
    # 16 = STATE BANK OF INDIA
    # 17 = THE SURAT PEOPLE
    # 18 = UJJVALA BANK
    # 19 = UNION BANK
    # 20 = VARCHHA BANK

    findPatternForBank()

    print("Tables extracted and saved to", csv_output)


if __name__ == "__main__":
    main()
