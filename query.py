import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('bankers_algo.db')
cursor = conn.cursor()

# Fetch all data from the resources table
cursor.execute('SELECT * FROM resources')
rows = cursor.fetchall()

# Display the stored data
if rows:
    print("Data in 'resources' table:")
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Number of Processes: {row[1]}")
        print(f"Number of Resources: {row[2]}")
        print(f"Available Resources: {row[3]}")
        print(f"Allocation: {row[4]}")
        print(f"Max Allocation: {row[5]}")
        print("-" * 30)
else:
    print("No data found in 'resources' table.")

# Close the database connection
conn.close()
