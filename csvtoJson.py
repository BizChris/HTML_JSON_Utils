import csv
import json

def csv_to_json(csv_file_path, json_file_path):
    # Create an empty list to store the rows
    rows = []

    # Open the CSV file and read it
    with open(csv_file_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            rows.append(row)

    # Write the data to a JSON file
    with open(json_file_path, 'w') as json_file:
        json_file.write(json.dumps(rows, indent=4))

# Usage
csv_to_json('/Users/christopherdickson/Downloads/Product Library.csv', '/Users/christopherdickson/Downloads/Product Library.json')