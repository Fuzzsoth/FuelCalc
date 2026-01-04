# fuel_mileage.py
# A Python script to log and analyse fuel mileage and trip info.
# Author: Randall Hose

import csv # for CSV file handling
import argparse # for command-line argument parsing
from datetime import datetime
from zoneinfo import ZoneInfo 
from pathlib import Path

CSV_PATH = Path(__file__).parent / "mileage_log.csv" # Set the default CSV file path

def ensure_csv(): # Def to check if the CSV file exists, and create it with appropriate headers if not
    if not CSV_PATH.exists():
        with CSV_PATH.open("w", newline="", encoding="utf-8") as f: # Open the file for writing
            writer = csv.writer(f) # Create a CSV writer object
            writer.writerow([ # Write the header row to the CSV file
                "Timestamp",
                "Car",
                "Date",
                "Distance_km",
                "Fuel_l",
                "Km_per_l",
                "L_per_100km",
                "Notes",
            ])

def add_entry(car, date, distance_km, fuel_l, notes): # Def to add a new entry to the CSV file
    distance_km = float(distance_km) # Convert distance to float
    fuel_l = float(fuel_l) # Convert fuel to float
    km_per_l = distance_km / fuel_l if fuel_l > 0 else 0.0 # Calculate km per litre
    l_per_100km = (fuel_l / distance_km) * 100 if distance_km > 0 else 0.0 # Calculate litres per 100 km
    timestamp = datetime.now().isoformat() # Get current datetime as ISO string
    ensure_csv() # Ensure the CSV file exists and create it if not
    with CSV_PATH.open("a", newline="", encoding="utf-8") as f: # Open the CSV file for appending
        writer = csv.writer(f) # Create a CSV writer object
        writer.writerow([ # Write the new entry to the CSV file with formatting - 2 decimal places
            timestamp,
            car,
            date,
            f"{distance_km:.2f}",
            f"{fuel_l:.2f}",
            f"{km_per_l:.2f}",
            f"{l_per_100km:.2f}",
            notes,
        ])
    print(f"Saved entry: {distance_km:.2f} km, {fuel_l:.2f} L -> {km_per_l:.2f} km/L") # echo to the screen

def list_entries(): # Def to list all entries in the CSV file
    if not CSV_PATH.exists(): # Check if the CSV file exists
        print("No entries yet. Add one first.")
        return
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f: # Open the CSV file for reading
        reader = csv.DictReader(f) # Create a CSV DictReader object
        rows = list(reader) # Read all rows into a list
        headers = reader.fieldnames or [] # Get the header names
    if not rows: # If there are no data rows, then prompt
        print("No entries yet. Add one first.")
        return
    print(" | ".join(headers)) # Print the header row with a separator "|"
    for i, row in enumerate(rows, start=1): # Loop through each data row
        values = [row.get(h, "") for h in headers] # Get the values for each header
        print(f"{i}) " + " | ".join(values)) # Print each row with its index and a separator "|"
    return rows

def read_rows(): # Def to read all rows from the CSV file and return them as a list
    if not CSV_PATH.exists(): # Check if the CSV file exists
        return None
    with CSV_PATH.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)

def stats(): # Def to calculate and display simple statistics from the CSV file
    if not CSV_PATH.exists(): # Check if the CSV file exists
        print("No entries to analyze.")
        return
    from collections import defaultdict # Import defaultdict for easier aggregation
    sums = defaultdict(lambda: {"km_per_l_sum": 0.0, "count": 0}) # Initialise a defaultdict to hold sums and counts
    with CSV_PATH.open("r", encoding="utf-8") as f: # Open the CSV file for reading
        reader = csv.DictReader(f) # Create a CSV DictReader object
        for row in reader: # Loop through each row in the CSV file
            car = row.get("car", "Unknown") # Get the car name from the row
            try:
                kmpl = float(row.get("km_per_l") or 0) # Try to convert km_per_l to float
            except ValueError: # If conversion fails, set km/pl to 0.0
                kmpl = 0.0
            sums[car]["km_per_l_sum"] += kmpl # Accumulate the km/pl sum for the car
            sums[car]["count"] += 1 # Increment the count for the car
    if not sums: # Double-check if we have any data
        print("No numeric data found.")
        return
    for car, data in sums.items(): # Loop through each car and its aggregated data
        avg = data["km_per_l_sum"] / data["count"] if data["count"] > 0 else 0.0 # Calculate average km/pl
        print(f"{car}: {avg:.2f} km/L over {data['count']} fill-ups") # Print the average and count for the car

def interactive_add(): # Def for interactive addition of a new entry
    cars = [] # List to hold known car names
    rows = read_rows() # Read existing rows from the CSV file
    if rows and len(rows) > 1: # If there are existing rows, then
        seen = set() # Set to track seen car names
        for r in rows[1:]: # Loop through each data row
            name = r[1] # Get the car name from the row
            if name and name not in seen: # If the car name is not empty and not already seen
                cars.append(name) # Add it to the list of known cars
                seen.add(name) # Mark it as seen
    if cars: # If we have known cars, prompt the user to choose one or enter a new one
        print("Known cars:")
        for idx, name in enumerate(cars, start=1): # List known cars with indexes
            print(f"{idx}) {name}") # Print each car with its index
        choice = input("Choose car number or press Enter to type a new car: ").strip() # Prompt user for choice or new car
        if choice.isdigit() and 1 <= int(choice) <= len(cars): # If the choice is a valid index
            car = cars[int(choice) - 1] # Select the car from the list
        else:
            car = input("Car (e.g., 'Toyota Camry'): ").strip() # Otherwise prompt user to enter a new car name
    else:
        car = input("Car (e.g., 'Toyota Camry'): ").strip() # Otherwise prompt user to enter a new car name
    date = input(f"Date (DD/MM/YYYY) [default {datetime.now().strftime('%d/%m/%Y')}]: ").strip() # Prompt user for date with default to today
    distance = input("Distance since last fill (km): ").strip() # Prompt user for distance in km
    fuel = input("Fuel added (litres): ").strip() # Prompt user for fuel in litres
    notes = input("Notes (weather, location, etc.) [optional]: ").strip() # Prompt user for optional notes
    add_entry(car, date, distance, fuel, notes) # Call add_entry to save the new entry

def remove_interactive(): # Def for interactive removal of an existing entry
    rows = read_rows() # Read existing rows from the CSV file
    if not rows or len(rows) <= 1: # If there are no data rows, then prompt
        print("No entries to remove.")
        return
    headers = rows[0] # Get the header row
    for i, r in enumerate(rows[1:], start=1): # Loop through each data row
        print(f"{i}) " + " | ".join(r)) # and print it with an index and a separator "|"
    choice = input("Enter entry number to delete (or 'q' to cancel): ").strip() # Prompt user for entry number to delete
    if choice.lower() == 'q': # If user chooses to cancel
        print("Cancelled")
        return
    if not choice.isdigit(): # If the choice is not a digit
        print("Invalid selection")
        return
    idx = int(choice) # Convert choice to integer
    delete_by_index(idx) # Call delete_by_index to remove the selected entry

def delete_by_index(idx): # Def to delete an entry by its index
    rows = read_rows() # Read existing rows from the CSV file
    if not rows or len(rows) <= 1: # If there are no data rows, then prompt
        print("No entries to delete.")
        return
    if idx < 1 or idx > len(rows) - 1: # If the index is out of range
        print("Index out of range")
        return
    to_remove = rows[idx] # Get the row to be removed
    confirm = input(f"Delete entry {idx}: {to_remove}? (y/N): ").strip().lower() # Prompt user for confirmation
    if confirm != 'y': # If user does not confirm
        print("Aborted")
        return
    new_rows = [rows[0]] + [r for i, r in enumerate(rows[1:], start=1) if i != idx] # Create a new list of rows excluding the one to be removed
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f: # Open the CSV file for writing
        writer = csv.writer(f) # Create a CSV writer object
        writer.writerows(new_rows) # Write the new rows to the CSV file
    print("Entry deleted")

def delete_by_timestamp(ts): # Def to delete an entry by its exact timestamp
    rows = read_rows() # Read existing rows from the CSV file
    if not rows or len(rows) <= 1: # If there are no data rows, then prompt
        print("No entries to delete.")
        return
    found = False # Flag to track if the timestamp was found
    new_rows = [rows[0]] # Start new rows with the header
    for r in rows[1:]: # Loop through each data row
        if r[0] == ts and not found: # If the timestamp matches and we haven't found it yet
            found = True # Mark as found
            continue # Skip adding this row to the new list
        new_rows.append(r) # Otherwise, add the row to the new list
    if not found: # If the timestamp was not found
        print("Timestamp not found")
        return
    with CSV_PATH.open("w", newline="", encoding="utf-8") as f: # Open the CSV file for writing
        writer = csv.writer(f) # Create a CSV writer object
        writer.writerows(new_rows) # Write the new rows to the CSV file
    print("Entry deleted")

def main(): # Main function to parse arguments and execute appropriate actions from the command line
    parser = argparse.ArgumentParser(description="Fuel mileage logger") # Create an argument parser
    parser.add_argument("--add", action="store_true", help="Interactive add") # Add argument for interactive addition
    parser.add_argument("--list", action="store_true", help="List all entries") # Add argument for listing entries
    parser.add_argument("--remove", action="store_true", help="Interactive remove") # Add argument for interactive removal
    parser.add_argument("--delete", type=int, help="Delete entry by row number (from --list)") # Add argument for deleting by index
    parser.add_argument("--delete-ts", type=str, help="Delete entry by exact timestamp string") # Add argument for deleting by timestamp
    parser.add_argument("--csv", type=str, help="Path to CSV file (overrides default)") # Add argument for specifying CSV file path
    parser.add_argument("--stats", action="store_true", help="Show simple stats") # Add argument for showing statistics
    args = parser.parse_args() # Parse the command-line arguments
    if args.csv: # If a CSV path is provided, override the default
        global CSV_PATH
        CSV_PATH = Path(args.csv)
    if args.add: # If interactive add is requested
        interactive_add()
        return
    if args.remove: # If interactive remove is requested
        remove_interactive()
        return
    if args.delete is not None: # If delete by index is requested
        delete_by_index(int(args.delete))
        return
    if args.delete_ts: # If delete by timestamp is requested
        delete_by_timestamp(args.delete_ts)
        return
    if args.list: # If list entries is requested
        list_entries()
        return
    if args.stats: # If stats is requested
        stats()
        return
    # default interactive menu
    while True: # Loop for the interactive menu
        print("\nFuel Mileage Logger")
        print("1) Add entry")
        print("2) List entries")
        print("3) Stats")
        print("4) Delete entry")
        print("5) Exit")
        choice = input("Choose: ").strip() # Prompt user for choice
        if choice == "1":
            interactive_add()
        elif choice == "2":
            list_entries()
        elif choice == "3":
            stats()
        elif choice == "4":
            remove_interactive()
        elif choice == "5":
            break
        else:
            print("Invalid choice") # Handle invalid choice

if __name__ == "__main__": # Entry point for the script
    main() # Call the main function
