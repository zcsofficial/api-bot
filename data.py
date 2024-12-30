import pymongo
import json
from tabulate import tabulate

# MongoDB connection details
client = pymongo.MongoClient('mongodb+srv://ebantisuser:pyPqVDQDR50RYRV@ebantis.y2lgplz.mongodb.net')
db = client['EbantisLogs']  # Database name
collection = db['ProductiveReport']  # Collection name

# File to store dumped data
dump_file = 'ProductiveReport_dump.json'

def dump_data_to_json(output_file):
    """
    Dumps all data from the MongoDB collection into a JSON file.
    """
    try:
        # Fetch all documents from the collection
        data = list(collection.find())
        
        # Convert MongoDB ObjectId to string for JSON serialization
        for record in data:
            if '_id' in record:
                record['_id'] = str(record['_id'])
        
        # Write data to JSON file
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        
        print(f"Data successfully exported to {output_file}")
    except Exception as e:
        print(f"Error exporting data: {e}")

def load_dumped_data():
    """
    Load the data from the JSON file.
    """
    try:
        with open(dump_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading dumped data: {e}")
        return []

def search_and_display_data(data, keyword):
    """
    Search for records matching the keyword in the loaded data and display them in a table.
    """
    try:
        # Flatten nested 'Report' structures in the data
        flattened_data = []
        for record in data:
            report_entries = record.get("Report", [])
            for entry in report_entries:
                flattened_data.append(entry)
        
        # Filter records containing the keyword in `EmployeeCode` or `UserName`
        filtered_data = [
            record for record in flattened_data
            if keyword.lower() in record.get('EmployeeCode', '').lower()
            or keyword.lower() in record.get('UserName', '').lower()
        ]
        
        if not filtered_data:
            print(f"No records found for keyword: '{keyword}'")
            return
        
        # Prepare data for tabular display
        table_data = []
        for record in filtered_data:
            table_data.append([
                record.get('EmployeeTransactionId', '-'),
                record.get('EmployeeCode', '-'),
                record.get('UserName', '-'),
                record.get('Leave', '-'),
                record.get('Installation', '-'),
                record.get('ProductivityRatio', '-'),
                record.get('totalTime', '-'),
                record.get('ActiveTime', '-'),
                record.get('UndefinedTime', '-')
            ])
        
        # Define table headers
        headers = [
            "Transaction ID", "Employee Code", "User Name", "Leave Status",
            "Installation", "Productivity Ratio", "Total Time", 
            "Active Time", "Undefined Time"
        ]
        
        print("\nMatching Records:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    except Exception as e:
        print(f"Error searching and displaying data: {e}")

def main():
    # Step 1: Dump data from MongoDB to JSON
    print("Dumping data from MongoDB...")
    dump_data_to_json(dump_file)

    # Step 2: Load the dumped data
    data = load_dumped_data()
    
    if not data:
        print("No data available to search.")
        return
    
    # Step 3: Interactive search
    while True:
        print("\n--- Employee Productivity Report Viewer ---")
        keyword = input("Enter a keyword to search (or type 'exit' to quit): ").strip()
        if keyword.lower() == 'exit':
            print("Exiting the program.")
            break
        search_and_display_data(data, keyword)

if __name__ == "__main__":
    main()
