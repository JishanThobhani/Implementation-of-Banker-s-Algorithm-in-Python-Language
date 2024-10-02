import numpy as np
import tkinter as tk
from tkinter import messagebox
import sqlite3

# SQLite database setup
conn = sqlite3.connect('bankers_algo.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS resources (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_processes INTEGER,
    num_resources INTEGER,
    available TEXT,
    allocation TEXT,
    max_allocation TEXT
)
''')

def save_data(num_processes, num_resources, available, allocation, max_allocation):
    cursor.execute('''
        INSERT INTO resources (num_processes, num_resources, available, allocation, max_allocation)
        VALUES (?, ?, ?, ?, ?)
    ''', (num_processes, num_resources, ' '.join(map(str, available)),
          '\n'.join(' '.join(map(str, row)) for row in allocation),
          '\n'.join(' '.join(map(str, row)) for row in max_allocation)))
    conn.commit()

def load_data():
    cursor.execute('SELECT * FROM resources ORDER BY id DESC LIMIT 1')
    row = cursor.fetchone()
    if row:
        return {
            'num_processes': row[1],
            'num_resources': row[2],
            'available': np.array([int(x) for x in row[3].split()]),
            'allocation': np.array([[int(x) for x in line.split()] for line in row[4].split('\n')]),
            'max_allocation': np.array([[int(x) for x in line.split()] for line in row[5].split('\n')])
        }
    else:
        return None

# Validating inputs
def valid_input(entry): 
    try:
        value = int(entry.get())
        if value < 0:
            raise ValueError("Negative value entered.")
        return True
    except ValueError:
        messagebox.showerror("Error", "Either value field is empty or having a negative value")
        return False

def valid_resource_inp(entry):
    try:
        values = [int(x) for x in entry.get().split()]
        if any(value < 0 for value in values):
            raise ValueError("Negative value entered.")
        return True
    except ValueError:
        messagebox.showerror("Error", "Either value field is empty or having a negative value")
        return False

def valid_allocation_inp(entry):
    try:
        rows = entry.get().split("\n")
        for row in rows:
            values = [int(x) for x in row.split()]
            if any(value < 0 for value in values):
                raise ValueError("Negative value entered.")
        return True
    except ValueError:
        messagebox.showerror("Error", "Either value field is empty or having a negative value")
        return False

def valid_request_inp(entry):
    try:
        values = [int(x) for x in entry.get().split()]
        if any(value < 0 for value in values):
            raise ValueError("Negative value entered.")
        return True
    except ValueError:
        messagebox.showerror("Error", "Please enter valid non-negative integers")
        return False

def valid_process_indx(entry, num_processes):
    try:
        index = int(entry.get())
        if index < 0 or index >= num_processes:
            raise ValueError("Invalid process index.")
        return True
    except ValueError:
        messagebox.showerror("Error", f"Please enter a valid process index between 0 and {num_processes - 1}.")
        return False

# Banker's Algorithm
def safety_algo(available, allocation, need, processes):
    w = available.copy()
    finish = np.zeros(len(processes), dtype=bool)
    safe_seq = []
    
    while len(safe_seq) < len(processes):
        found = False
        for i, process in enumerate(processes):
            if not finish[i] and all(need[i] <= w):
                w += allocation[i]
                finish[i] = True
                safe_seq.append(process)
                found = True
        if not found:
            return None, None
    return safe_seq, need

def resource_request_algo(available, allocation, need, process_index, request, processes):
    if all(request <= need[process_index]) and all(request <= available):
        available -= request
        allocation[process_index] += request
        need[process_index] -= request
        safe_seq, new_need = safety_algo(available, allocation, need, processes)
        if safe_seq is not None:
            return "Request can be granted. Safe sequence: " + ", ".join(safe_seq), new_need
        else:
            available += request
            allocation[process_index] -= request
            need[process_index] += request
            return "Request cannot be granted because it results into an unsafe state.", None
    else:
        return "Request cannot be granted due to insufficient resources or exceeding need.", None

# Function to dynamically generate fields for the processes based on user input
def generate_process_fields():
    if not valid_input(num_processes_entry) or not valid_input(num_resources_entry):
        return

    num_processes = int(num_processes_entry.get())
    num_resources = int(num_resources_entry.get())

    # Clear previous entries
    for widget in process_frame.winfo_children():
        widget.destroy()

    # Generate fields dynamically
    global allocation_entries, max_allocation_entries
    allocation_entries = []
    max_allocation_entries = []

    for i in range(num_processes):
        allocation_label = tk.Label(process_frame, text=f"Allocation for Process {i}:")
        allocation_label.grid(row=i, column=0)
        allocation_entry = tk.Entry(process_frame)
        allocation_entry.grid(row=i, column=1)
        allocation_entries.append(allocation_entry)

        max_allocation_label = tk.Label(process_frame, text=f"Max Allocation for Process {i}:")
        max_allocation_label.grid(row=i, column=2)
        max_allocation_entry = tk.Entry(process_frame)
        max_allocation_entry.grid(row=i, column=3)
        max_allocation_entries.append(max_allocation_entry)

# Main Function to Run the Algorithm
def run_algo():
    if not valid_input(num_resources_entry) or not valid_input(num_processes_entry):
        return

    if not valid_resource_inp(available_entry):
        return

    for entry in allocation_entries:
        if not valid_allocation_inp(entry):
            return

    for entry in max_allocation_entries:
        if not valid_allocation_inp(entry):
            return

    if request_process_entry.get() != "" and not valid_request_inp(request_entry):
        return

    num_resources_str = num_resources_entry.get()
    num_processes_str = num_processes_entry.get()
    request_process_str = request_process_entry.get()

    if num_resources_str == "" or num_processes_str == "":
        messagebox.showerror("Error", "Please enter values for all fields.")
        return

    num_resources = int(num_resources_str)
    num_processes = int(num_processes_str)
    
    available_values = available_entry.get().split()
    if len(available_values) != num_resources:
        messagebox.showerror("Error", "Number of values for available resources doesn't match the specified number of resources.")
        return

    available = np.array([int(x) for x in available_values])
    
    allocation = np.zeros((num_processes, num_resources), dtype=int)
    for i in range(num_processes):
        allocation_values = allocation_entries[i].get().split()
        if len(allocation_values) != num_resources:
            messagebox.showerror("Error", f"Number of values for allocation of Process {i} doesn't match the specified number of resources.")
            return
        allocation[i] = [int(x) for x in allocation_values]
    
    max_allocation = np.zeros((num_processes, num_resources), dtype=int)
    for i in range(num_processes):
        max_allocation_values = max_allocation_entries[i].get().split()
        if len(max_allocation_values) != num_resources:
            messagebox.showerror("Error", f"Number of values for max allocation of Process {i} doesn't match the specified number of resources.")
            return
        max_allocation[i] = [int(x) for x in max_allocation_values]
    
    need = max_allocation - allocation
    
    processes = [str(i) for i in range(num_processes)]

    if np.any(allocation > max_allocation):
        messagebox.showerror("Error", "Allocation cannot exceed maximum allocation.")
        return
    
    # Save the current state to the database
    save_data(num_processes, num_resources, available, allocation, max_allocation)

    # Running the safety algorithm
    safe_seq, need = safety_algo(available, allocation, need, processes)
    if safe_seq is not None:
        safe_seq_label.config(text="Safe sequence: " + ", ".join(safe_seq), fg="green")
    else:
        safe_seq_label.config(text="System is in an unsafe state.", fg="red")
    
    need_label.config(text="Need Matrix:\n" + "\n".join(" ".join(str(x) for x in row) for row in need))

    # Running resource request
    if request_process_str != "":
        process_index = int(request_process_str)
        request_values = request_entry.get().split()
        if len(request_values) != num_resources:
            messagebox.showerror("Error", "Number of values for request doesn't match the specified number of resources.")
            return
        request = np.array([int(x) for x in request_values])

        message, new_need = resource_request_algo(available, allocation, need, process_index, request, processes)
        messagebox.showinfo("Result", message)
        if new_need is not None:
            need_label.config(text="Updated Need Matrix:\n" + "\n".join(" ".join(str(x) for x in row) for row in new_need))

# GUI Setup
root = tk.Tk()
root.title("Banker's Algorithm")
root.geometry("600x600")

frame_color = "#333"
entry_color = "#FFF"
label_color = "#FFF"
button_color = "#0066CC"
bg_color = "#444"

root.configure(bg=bg_color)

inp_frame = tk.Frame(root, bg=frame_color)
inp_frame.pack(pady=20)

process_frame = tk.Frame(root, bg=bg_color)
process_frame.pack(pady=10)

num_resources_label = tk.Label(inp_frame, text="Number of Resources:", bg=frame_color, fg=label_color)
num_resources_label.grid(row=0, column=0)
num_resources_entry = tk.Entry(inp_frame, bg=entry_color)
num_resources_entry.grid(row=0, column=1)

num_processes_label = tk.Label(inp_frame, text="Number of Processes:", bg=frame_color, fg=label_color)
num_processes_label.grid(row=1, column=0)
num_processes_entry = tk.Entry(inp_frame, bg=entry_color)
num_processes_entry.grid(row=1, column=1)

generate_button = tk.Button(inp_frame, text="Generate Fields", command=generate_process_fields, bg=button_color, fg="white")
generate_button.grid(row=2, columnspan=4, pady=10)

available_label = tk.Label(inp_frame, text="Available Resources:", bg=frame_color, fg=label_color)
available_label.grid(row=3, column=0)
available_entry = tk.Entry(inp_frame, bg=entry_color)
available_entry.grid(row=3, column=1)

request_process_label = tk.Label(inp_frame, text="Request for Process:", bg=frame_color, fg=label_color)
request_process_label.grid(row=4, column=0)
request_process_entry = tk.Entry(inp_frame, bg=entry_color)
request_process_entry.grid(row=4, column=1)

request_label = tk.Label(inp_frame, text="Request Resources:", bg=frame_color, fg=label_color)
request_label.grid(row=5, column=0)
request_entry = tk.Entry(inp_frame, bg=entry_color)
request_entry.grid(row=5, column=1)

run_button = tk.Button(inp_frame, text="Run Banker's Algorithm", command=run_algo, bg=button_color, fg="white")
run_button.grid(row=6, columnspan=4, pady=10)

safe_seq_label = tk.Label(root, text="Safe Sequence: ", bg=bg_color, fg=label_color)
safe_seq_label.pack()

need_label = tk.Label(root, text="Need Matrix: ", bg=bg_color, fg=label_color)
need_label.pack()

root.mainloop()

conn.close()
