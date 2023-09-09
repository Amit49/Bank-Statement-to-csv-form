import sys
import akand_anand_bank
import axis_bank
import bank_of_baroda

csv_output = ""

def findPatternForBank():
    global csv_output
    
    pdf_file = sys.argv[1]
    csv_output = sys.argv[2]
    bank_name = sys.argv[3].lower()
    if bank_name == "akhand anand bank" or bank_name == "akhand anand":
        akand_anand_bank.initialize(pdf_file, csv_output)
    elif bank_name == "axis bank" or bank_name == "axis":
        axis_bank.initialize(pdf_file, csv_output)
    elif bank_name == "bank of baroda" or bank_name == "baroda" or bank_name == "bob":
        bank_of_baroda.initialize(pdf_file, csv_output)
    else:
        print("Bank not found")
def main():
    if len(sys.argv) != 4:
        print("Usage: python script.py <pdf_file> <csv_output> <bank_name>")
        return
    
    findPatternForBank()

    print("Tables extracted and saved to", csv_output)


if __name__ == "__main__":
    main()
