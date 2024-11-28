############################################################
#  Name: gui.py
#  Date: 28.11.2024       Authors: Ali Berk Karaarslan
#  Description: Graphical User Interface Of STMS Database   
############################################################

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from concurrent.futures import ThreadPoolExecutor
import requests

# Create a persistent HTTP session
session = requests.Session()

# List of database tables
dbTables = []
entry_fields = []  # Stores dynamic input fields
selected_row = None  # Holds information about the selected row
selected_table = None  # Currently selected table

# Button references for dynamic UI updates
add_button = None
clear_button = None
save_button = None
remove_button = None
edit_button = None

editingEntity = False  # Tracks if the user is editing an entity

# Create a thread pool executor with a limited number of worker threads
executor = ThreadPoolExecutor(max_workers=5)

# Initialize the database connection and fetch tables
def initialize():
    executor.submit(initialize_thread)

def initialize_thread():
    try:
        global dbTables
        response = session.get('http://localhost:5000/tables', timeout=10)
        if response.status_code == 200:
            dbTables = response.json()['tables']
            # Update the table_listbox in the main thread
            root.after(0, populate_table_listbox)
        else:
            error_message = response.json().get('error', 'Failed to fetch tables')
            root.after(0, show_error_message, error_message)
    except requests.exceptions.RequestException as e:
        root.after(0, show_error_message, f"API request failed: {e}")

def populate_table_listbox():
    # Clear existing entries
    table_listbox.delete(0, tk.END)
    # Populate listbox with table names
    for table in dbTables:
        table_listbox.insert(tk.END, table)

# Show error messages in a popup dialog
def show_error_message(error_text):
    messagebox.showerror("Error", error_text)

# Clear input fields and reset buttons to default state
def clear_fields():
    global selected_row, editingEntity
    global add_button, clear_button, save_button, remove_button, edit_button

    selected_row = None
    editingEntity = False

    # Clear all input fields
    for _, entry in entry_fields:
        entry.delete(0, tk.END)

    # Clear selection in Treeview
    for item in tree.selection():
        tree.selection_remove(item)

    # Reset buttons for adding data
    reset_buttons()

    add_button = tk.Button(input_frame, text="Add", command=add_data)
    add_button.pack(side=tk.LEFT, padx=5, pady=5)

    clear_button = tk.Button(input_frame, text="Clear", command=clear_fields)
    clear_button.pack(side=tk.LEFT, padx=5, pady=5)

# Create input fields dynamically based on table schema
def create_attribute_fields(table_name):
    global add_button, clear_button, save_button, remove_button, edit_button

    try:
        # Clear any existing widgets in the input frame
        for widget in input_frame.winfo_children():
            widget.destroy()
        entry_fields.clear()

        # Scrollable frame for input fields
        canvas = tk.Canvas(input_frame, height=200)
        scrollbar = ttk.Scrollbar(input_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Fetch the schema of the selected table from API
        def fetch_schema():
            try:
                response = session.get(f'http://localhost:5000/schema/{table_name}', timeout=10)
                if response.status_code == 200:
                    columns = response.json()['schema']
                    root.after(0, create_fields, columns)
                else:
                    error_message = response.json().get('error', 'Failed to fetch schema')
                    root.after(0, show_error_message, error_message)
            except requests.exceptions.RequestException as e:
                root.after(0, show_error_message, f"API request failed: {e}")

        executor.submit(fetch_schema)

        # Arrange fields in two columns
        def create_fields(columns):
            for i, col in enumerate(columns):
                col_name = col['Field']
                row, column = divmod(i, 2)

                label = tk.Label(scrollable_frame, text=col_name)
                label.grid(row=row, column=2 * column, padx=5, pady=5, sticky=tk.W)

                entry = tk.Entry(scrollable_frame)
                entry.grid(row=row, column=2 * column + 1, padx=5, pady=5, sticky=tk.W)
                entry_fields.append((col_name, entry))

            # Reset buttons
            reset_buttons()

            # Create Add and Clear buttons
            add_button = tk.Button(input_frame, text="Add", command=add_data)
            add_button.pack(side=tk.LEFT, padx=5, pady=5)

            clear_button = tk.Button(input_frame, text="Clear", command=clear_fields)
            clear_button.pack(side=tk.LEFT, padx=5, pady=5)

    except Exception as e:
        root.after(0, show_error_message, f"Error: {e}")

# Fetch table data and populate the Treeview
def fetch_data(table_name):
    executor.submit(fetch_data_thread, table_name)

def fetch_data_thread(table_name):
    try:
        response = session.get(f'http://localhost:5000/data/{table_name}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            columns = data['columns']
            rows = data['data']
            # Update the treeview in the main thread
            root.after(0, update_treeview, columns, rows)
        else:
            error_message = response.json().get('error', 'Failed to fetch data')
            root.after(0, show_error_message, error_message)
    except requests.exceptions.RequestException as e:
        root.after(0, show_error_message, f"API request failed: {e}")

def update_treeview(columns, rows):
    # Update the Treeview widget
    tree["columns"] = columns
    tree.delete(*tree.get_children())
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100)
    for row in rows:
        values = [row.get(col) for col in columns]
        tree.insert("", tk.END, values=values)

def add_data():
    executor.submit(add_data_thread)

def add_data_thread():
    global selected_table
    if not selected_table:
        return

    # Collect data from input fields
    record = {col_name: entry.get() for col_name, entry in entry_fields}

    data = {
        'table_name': selected_table,
        'record': record
    }

    try:
        response = session.post('http://localhost:5000/add_data', json=data, timeout=10)
        if response.status_code == 200:
            message = response.json().get('message', 'Data added successfully')
            # Show success message in main thread
            root.after(0, messagebox.showinfo, "Success", message)
            # Refresh data
            fetch_data(selected_table)
            root.after(0, clear_fields)
        else:
            error_message = response.json().get('error', 'Failed to add data')
            root.after(0, show_error_message, error_message)
    except requests.exceptions.RequestException as e:
        root.after(0, show_error_message, f"API request failed: {e}")

# Fill input fields with data from the selected row
def fill_fields():
    global selected_row, selected_table, editingEntity
    global add_button, clear_button, save_button, remove_button, edit_button

    if not selected_table:
        return

    selected_item = tree.selection()
    if not selected_item:
        return

    # Get selected row data
    selected_row = tree.item(selected_item)["values"]

    for i, (col_name, entry) in enumerate(entry_fields):
        if i < len(selected_row):
            entry.delete(0, tk.END)
            entry.insert(0, selected_row[i])

    editingEntity = True

    # Update buttons for edit mode
    reset_buttons()

    save_button = tk.Button(input_frame, text="Save", command=save_updated_data)
    save_button.pack(side=tk.LEFT, padx=5, pady=5)

    clear_button = tk.Button(input_frame, text="Cancel", command=clear_fields)
    clear_button.pack(side=tk.LEFT, padx=5, pady=5)

    remove_button = tk.Button(input_frame, text="Remove", command=remove_data)
    remove_button.pack(side=tk.LEFT, padx=5, pady=5)

# Update an existing record in the selected table
def save_updated_data():
    executor.submit(save_updated_data_thread)

def save_updated_data_thread():
    global selected_table, selected_row

    if not selected_table or not selected_row:
        return

    # Prepare the data payload
    record = {col_name: entry.get() for col_name, entry in entry_fields}
    key = {entry_fields[0][0]: selected_row[0]}  # Assuming first field is primary key

    data = {
        'table_name': selected_table,
        'record': record,
        'key': key
    }

    try:
        response = session.put('http://localhost:5000/update_data', json=data, timeout=10)
        if response.status_code == 200:
            message = response.json().get('message', 'Data updated successfully')
            root.after(0, messagebox.showinfo, "Success", message)
            fetch_data(selected_table)
            root.after(0, clear_fields)
        else:
            error_message = response.json().get('error', 'Failed to update data')
            root.after(0, show_error_message, error_message)
    except requests.exceptions.RequestException as e:
        root.after(0, show_error_message, f"API request failed: {e}")

# Remove the selected row from the database
def remove_data():
    executor.submit(remove_data_thread)

def remove_data_thread():
    global selected_table, selected_row

    if not selected_table or not selected_row:
        return

    key = {entry_fields[0][0]: selected_row[0]}  # Assuming first field is primary key
    data = {
        'table_name': selected_table,
        'key': key
    }

    try:
        response = session.delete('http://localhost:5000/delete_data', json=data, timeout=10)
        if response.status_code == 200:
            message = response.json().get('message', 'Data deleted successfully')
            root.after(0, messagebox.showinfo, "Success", message)
            fetch_data(selected_table)
            root.after(0, clear_fields)
        else:
            error_message = response.json().get('error', 'Failed to delete data')
            root.after(0, show_error_message, error_message)
    except requests.exceptions.RequestException as e:
        root.after(0, show_error_message, f"API request failed: {e}")

# Reset all buttons to default state
def reset_buttons():
    global add_button, clear_button, save_button, remove_button, edit_button

    if add_button:
        add_button.pack_forget()
    if clear_button:
        clear_button.pack_forget()
    if save_button:
        save_button.pack_forget()
    if remove_button:
        remove_button.pack_forget()
    if edit_button:
        edit_button.pack_forget()

# Handle table selection from the listbox
def on_table_select(event):
    global selected_table

    # Get the selected table name
    selection = table_listbox.curselection()
    if not selection:
        return

    selected_table = table_listbox.get(selection)

    if selected_table:
        # Load the table data and its attributes
        fetch_data(selected_table)
        create_attribute_fields(selected_table)

# Clear selection in Treeview if clicked outside of it
def clear_tree_selection(event):
    global selected_row

    # Check if the click is outside the Treeview or buttons, and if a row is selected
    if event.widget != tree and not isinstance(event.widget, tk.Button) and selected_row is not None and not editingEntity:
        for item in tree.selection():
            tree.selection_remove(item)
        selected_row = None
        clear_fields()

# Update buttons when a row in Treeview is selected
def show_update_button(event):
    global selected_row, selected_table
    global add_button, clear_button, save_button, remove_button, edit_button

    if not selected_table:
        return

    # Get the selected item in Treeview
    selected_item = tree.selection()
    if not selected_item:
        return

    selected_row = tree.item(selected_item)["values"]

    # Update buttons for edit mode
    reset_buttons()

    edit_button = tk.Button(input_frame, text="Edit", command=fill_fields)
    edit_button.pack(side=tk.LEFT, padx=5, pady=5)

    remove_button = tk.Button(input_frame, text="Remove", command=remove_data)
    remove_button.pack(side=tk.LEFT, padx=5, pady=5)

# Tkinter GUI setup
root = tk.Tk()
root.title("STMS Database Management Tool")
root.geometry("1000x600")

# Left section: Listbox for tables
table_listbox = tk.Listbox(root, height=30, width=30)
table_listbox.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

# Top-right section: Dynamic input fields
input_frame = tk.Frame(root)
input_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

# Bottom-right section: Treeview for table data
tree = ttk.Treeview(root, show="headings")
tree.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

# Bind table selection event
table_listbox.bind("<<ListboxSelect>>", on_table_select)

# Bind Treeview selection event
tree.bind("<<TreeviewSelect>>", show_update_button)

# Initialize dynamic buttons (hidden initially)
add_button = tk.Button(input_frame, text="Add", command=add_data)
save_button = tk.Button(input_frame, text="Save", command=save_updated_data)
remove_button = tk.Button(input_frame, text="Remove", command=remove_data)
clear_button = tk.Button(input_frame, text="Clear", command=clear_fields)
edit_button = tk.Button(input_frame, text="Edit", command=fill_fields)

# Bind click event to clear Treeview selection when clicking outside
root.bind("<Button-1>", clear_tree_selection)

# Start the initialization and the Tkinter event loop
initialize()
root.mainloop()
