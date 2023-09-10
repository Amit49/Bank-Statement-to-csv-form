import os
import csv
import subprocess


# Directory containing PDF files and its subdirectories
root_directory = 'COMPLETE_04.09.2023'

# Create a list of PDF file names in the directory and its subdirectories
pdf_files = []
for root, dirs, files in os.walk(root_directory):
    for filename in files:
        if filename.endswith('.pdf'):
            pdf_files.append(os.path.join(root, filename))

# Name of the CSV file to create
csv_filename = 'pdf_files.csv'


# Write the PDF file names to the CSV file
with open(csv_filename, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(['PDF File Name'])  # Header row

    for pdf_file in pdf_files:
        # Define the arguments you want to pass to script_to_run.py
        arg1 = pdf_file
        arg2 = pdf_file[:-4]+".csv"
        # Use subprocess to call script_to_run.py
        try:
            subprocess.run(["python", "table_to_csv.py", arg1, arg2], check=True)
            
        except subprocess.CalledProcessError:
            print("Error running script_to_run.py")

        csv_writer.writerow([pdf_file])

print(f'{len(pdf_files)} PDF file names written to {csv_filename}.')