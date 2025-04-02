import pyrebase
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Import ttk for the notebook (tabs)
import json
import csv
from tkinter import filedialog  # Corrected filedialog import
import firebase_admin
from firebase_admin import credentials , db


# firebaseConfig = {
#     "apiKey": "AIzaSyC7TSOG32sU0uzDHwziTPwpKkStG9gk8PI",
#     "authDomain": "npkdetection.firebaseapp.com",
#     "databaseURL": "https://npkdetection-default-rtdb.firebaseio.com/",
#     "projectId": "npkdetection",
#     "storageBucket": "npkdetection.appspot.com",
#     "messagingSenderId": "392510783096",
#     "appId": "1:392510783096:web:1336efa61f7372ba17378d",
#     "measurementId": "G-EWKL268L7N"
# }
# Use raw string to avoid escape character issues
cred_path = r"D:\IIT Kgp\Sem2\EAL\NPK\npkdetection-firebase-adminsdk-fbsvc-d770d993e9.json"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred, {
    "databaseURL":" https://npkdetection-default-rtdb.firebaseio.com/"
})

# firebase = pyrebase.initialize_app(firebaseConfig)
# db = firebase.database()

# Firebase Reference (define it here globally)
userdata_ref = db.reference("Initialization")

# Initialize the Tkinter window
root = tk.Tk()
root.title("NPK Detection Application")

# Set the window size
root.geometry("500x400")

# Create a Notebook widget (tabbed interface)
notebook = ttk.Notebook(root)
notebook.pack(pady=10, expand=True)

# Create the Initialization tab
init_frame = ttk.Frame(notebook)
notebook.add(init_frame, text="Initialization")

# Define Entry Fields for Sample Name and Sample Size with increased font size
sample_name_label = tk.Label(init_frame, text="Sample Name", font=("Arial", 14))
sample_name_label.grid(row=0, column=0, padx=20, pady=20)

sample_name_entry = tk.Entry(init_frame, font=("Arial", 14), width=20)
sample_name_entry.grid(row=0, column=1, padx=20, pady=20)

sample_size_label = tk.Label(init_frame, text="Sample Size", font=("Arial", 14))
sample_size_label.grid(row=1, column=0, padx=20, pady=20)

sample_size_entry = tk.Entry(init_frame, font=("Arial", 14), width=20)
sample_size_entry.grid(row=1, column=1, padx=20, pady=20)

# Status Label
status_label = tk.Label(init_frame, text="Status", font=("Arial", 14))
status_label.grid(row=2, column=0, padx=20, pady=20)

# Progress Bar
progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(init_frame, orient="horizontal", length=300, mode="determinate", variable=progress_var)
progress_bar.grid(row=2, column=1, padx=20, pady=20)

# Function to animate progress bar
def animate_progress():
    progress_bar.config(mode="indeterminate")
    progress_bar.start(10)  # Speed of animation

# Function to update Firebase when "Start" is pressed
def start_process():
    sample_name = sample_name_entry.get()
    sample_size = sample_size_entry.get()

    if not sample_name or not sample_size:
        messagebox.showerror("Input Error", "Please enter both sample name and sample size.")
        return

    try:
        # Update Firebase
        userdata_ref.update({
            "Start": True,
            "Sample_Name": sample_name,
            "Sample_Size": sample_size,
            "Status": "Ongoing"
        })
        messagebox.showinfo("Success", "Process started and data saved to Firebase.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update Firebase: {str(e)}")

# Function to update Firebase when "Stop" is pressed
def stop_process():
    try:
        # Update Firebase
        userdata_ref.update({
            "Start": False,
            "Status": "Done"
        })
        messagebox.showinfo("Success", "Process stopped and data updated in Firebase.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update Firebase: {str(e)}")

# Function to check status from Firebase and update UI
def check_status():
    try:
        status = userdata_ref.child("Status").get()
        
        if status == "Ongoing":
            progress_bar.config(mode="indeterminate")
            progress_bar.start(10)  # Start animation
        elif status == "Done":
            progress_bar.stop()
            progress_bar.config(mode="determinate")
            progress_var.set(100)  # Full progress bar
        else:
            progress_bar.stop()
            progress_bar.config(mode="determinate")
            progress_var.set(0)  # Reset bar
        
        # Schedule next check
        root.after(2000, check_status)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve status from Firebase: {str(e)}")

# Start monitoring Firebase status updates
root.after(1000, check_status)

# Start button to initiate the process
start_button = tk.Button(init_frame, text="Start", command=start_process, font=("Arial", 14), bg="green", fg="white")
start_button.grid(row=3, column=0, padx=20, pady=20)

# Stop button to stop the process
stop_button = tk.Button(init_frame, text="Stop", command=stop_process, font=("Arial", 14), bg="red", fg="white")
stop_button.grid(row=3, column=1, padx=20, pady=20)


# Create the Results tab
result_frame = ttk.Frame(notebook)
notebook.add(result_frame, text="Results")

# Function to fetch and display child keys of Soil_Data from Firebase
def show_soil_data_keys():
    try:
        soil_data_ref = db.child("Soil_Data")
        soil_data = soil_data_ref.get()

        for widget in soil_data_keys_frame.winfo_children():
            widget.destroy()

        if isinstance(soil_data.val(), dict):
            for key in soil_data.val().keys():
                frame = tk.Frame(soil_data_keys_frame)
                frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

                key_label = tk.Label(frame, text=key, font=("Arial", 12))
                key_label.pack(side=tk.LEFT, padx=10)

                def handle_option(selected_option, key=key):
                    if selected_option == "Download CSV":
                        download_csv(key)
                    elif selected_option == "Print Value":
                        print_value(key)

                options = ["Download CSV", "Print Value"]
                selected_option = tk.StringVar(value="Select Action")
                dropdown = tk.OptionMenu(frame, selected_option, *options, command=lambda opt, key=key: handle_option(opt, key))
                dropdown.pack(side=tk.RIGHT, padx=10)

        elif isinstance(soil_data.val(), list):
            for index, item in enumerate(soil_data.val()):
                frame = tk.Frame(soil_data_keys_frame)
                frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

                key_label = tk.Label(frame, text=f"Item {index + 1}", font=("Arial", 12))
                key_label.pack(side=tk.LEFT, padx=10)

                def handle_option(selected_option, index=index):
                    if selected_option == "Download CSV":
                        download_csv(index)
                    elif selected_option == "Print Value":
                        print_value(index)

                options = ["Download CSV", "Print Value"]
                selected_option = tk.StringVar(value="Select Action")
                dropdown = tk.OptionMenu(frame, selected_option, *options, command=lambda opt, index=index: handle_option(opt, index))
                dropdown.pack(side=tk.RIGHT, padx=10)

        else:
            messagebox.showinfo("No Data", "No soil data available.")

    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch Soil Data: {str(e)}")

# Function to download data as CSV for a specific key or index
def download_csv(identifier):
    try:
        # Reference to the specific data in Soil_Data
        soil_data_ref = db.child("Soil_Data").child(str(identifier))
        
        # Fetch the data for the selected key or index
        data = soil_data_ref.get().val()

        if data is not None:
             # Default filename using the identifier
            default_filename = f"{identifier}.csv"
            # Create a CSV file and write data to it
            file_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if file_path:
                with open(file_path, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Assuming data is a dictionary, write headers and rows
                    if isinstance(data, dict):
                        headers = data.keys()
                        writer.writerow(headers)  # Write the header row
                        writer.writerow(data.values())  # Write the data values
                    elif isinstance(data, list):
                        # If the data is a list, write the elements directly
                        writer.writerow(["Index", "Value"])  # You can change the headers accordingly
                        for index, value in enumerate(data):
                            writer.writerow([index, value])  # Write each element

                messagebox.showinfo("Success", f"CSV file saved as {file_path}")
        else:
            messagebox.showwarning("No Data", "No data available for this key.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to download CSV: {str(e)}")
# Function to print value from Firebase for a selected key
def print_value(identifier):
    try:
        soil_data_ref = db.child("results").child(str(identifier))
        data = soil_data_ref.get().val()
        if data is not None:
            print(f"Value for {identifier}: {data}")
            messagebox.showinfo("Value", f"Data for {identifier}:\n{json.dumps(data, indent=4)}")
        else:
            messagebox.showwarning("No Data", f"No data available for {identifier}.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")


# Create a frame for displaying the keys horizontally
canvas = tk.Canvas(result_frame)
scrollbar = tk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
soil_data_keys_frame = tk.Frame(canvas)

# Add the scrollbar to the canvas and bind scrolling
canvas.configure(yscrollcommand=scrollbar.set)

# Create a window inside the canvas to hold the keys
canvas.create_window((0, 0), window=soil_data_keys_frame, anchor="nw")
canvas.grid(row=0, column=0, sticky="nsew")
scrollbar.grid(row=0, column=1, sticky="ns")

# Button to load and show only the keys of Soil Data
fetch_soil_data_button = tk.Button(result_frame, text="Fetch Soil Data Keys", command=show_soil_data_keys, font=("Arial", 12))
fetch_soil_data_button.grid(row=1, column=0, pady=20)

# Configure the scroll region of the canvas
soil_data_keys_frame.update_idletasks()
canvas.config(scrollregion=canvas.bbox("all"))

# Start the Tkinter event loop
root.mainloop()
