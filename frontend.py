import tkinter as tk
from tkinter import messagebox, ttk
from parameters import *
import csv
from tkinter import filedialog 

class UI:
    def __init__(self, root, process_handler):
        self.root = root
        self.process_handler = process_handler
        self.root.title("NPK Detection Application")
        self.root.geometry("500x400")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, expand=True)

        self.init_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.init_frame, text="Initialization")

        self.result_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.result_frame, text="Results")

        self.setup_initialization_tab()
        self.setup_results_tab()

    def setup_initialization_tab(self):
        tk.Label(self.init_frame, text="Sample Name", font=("Arial", 14)).grid(row=0, column=0, padx=20, pady=20)
        self.sample_name_entry = tk.Entry(self.init_frame, font=("Arial", 14), width=20)
        self.sample_name_entry.grid(row=0, column=1, padx=20, pady=20)

        tk.Label(self.init_frame, text="Sample Size", font=("Arial", 14)).grid(row=1, column=0, padx=20, pady=20)
        self.sample_size_entry = tk.Entry(self.init_frame, font=("Arial", 14), width=20)
        self.sample_size_entry.grid(row=1, column=1, padx=20, pady=20)

        self.progress_var = tk.IntVar()
        self.progress_bar = ttk.Progressbar(self.init_frame, orient="horizontal", length=300, mode="determinate", variable=self.progress_var)
        self.progress_bar.grid(row=2, column=1, padx=20, pady=20)

        tk.Button(self.init_frame, text="Start", command=self.process_handler.start_process, font=("Arial", 14), bg="green", fg="white").grid(row=3, column=0, padx=20, pady=20)
        tk.Button(self.init_frame, text="Stop", command=self.process_handler.stop_process, font=("Arial", 14), bg="red", fg="white").grid(row=3, column=1, padx=20, pady=20)

    def setup_results_tab(self):
        self.canvas = tk.Canvas(self.result_frame)
        self.scrollbar = tk.Scrollbar(self.result_frame, orient="vertical", command=self.canvas.yview)
        self.soil_data_keys_frame = tk.Frame(self.canvas)
        
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.create_window((0, 0), window=self.soil_data_keys_frame, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.fetch_soil_data_button = tk.Button(self.result_frame, text="Fetch Soil Data Keys", command=self.process_handler.show_soil_data_keys, font=("Arial", 12))
        self.fetch_soil_data_button.grid(row=1, column=0, pady=20)
    
    def create_key_option_frame(self, key):
        frame = tk.Frame(self.soil_data_keys_frame)
        frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        key_label = tk.Label(frame, text=key, font=("Arial", 12))
        key_label.pack(side=tk.LEFT, padx=10)
        
        options = ["Download CSV", "Predict NPK"]
        selected_option = tk.StringVar(value="Select Action")
        dropdown = tk.OptionMenu(frame, selected_option, *options, command=lambda opt: self.process_handler.handle_option(opt, key))
        dropdown.pack(side=tk.RIGHT, padx=10)



class ProcessHandler:
    def __init__(self, firebase_handler, root, ui,base_instance):
        self.fb = firebase_handler
        self.root = root
        self.ui = ui 
        self.Backend = base_instance

    def start_process(self):
        Sample_Name = self.ui.sample_name_entry.get()
        Sample_Size = int(self.ui.sample_size_entry.get())
        if not Sample_Name or not Sample_Size:
            messagebox.showerror("Input Error", "Please enter both sample name and sample size.")
            return

        data = {'Sample_Name': Sample_Name, 'Sample_Size': Sample_Size, 'Start': True, 'Status': 'Ongoing'}

        self.Backend.collect(data)


    def stop_process(self):

        self.fb.user_ref.update({"Start": False, "Status": "Done"})
        messagebox.showinfo("Success", "Process stopped and data updated in Firebase.")

    def show_soil_data_keys(self):
        try:

            soil_data = self.fb.soil_ref.get() 

            for widget in self.ui.soil_data_keys_frame.winfo_children():
                widget.destroy()

            if soil_data and isinstance(soil_data, dict): 
                for child_name in soil_data.keys():  
                    self.ui.create_key_option_frame(child_name)
            else:
                messagebox.showinfo("No Data", "No soil data available or incorrect format.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch Soil Data: {str(e)}")
    

    def handle_option(self, selected_option, key):
        if selected_option == "Download CSV":
            self.download_csv(key)
        elif selected_option == "Predict NPK":
            self.print_value(key)
    
    def download_csv(self, Sample_Name):
        try:
            soil_data_ref = self.fb.soil_ref.child(str(Sample_Name))
            data = soil_data_ref.get()
            
            if data is not None:
                default_filename = f"{Sample_Name}.csv"
                file_path = filedialog.asksaveasfilename(initialfile=default_filename, defaultextension=".csv", filetypes=[["CSV files", "*.csv"]])
                if file_path:
                    with open(file_path, 'w', newline='') as csvfile:
                        writer = csv.writer(csvfile)
                        if isinstance(data, dict):
                            writer.writerow(data.keys())
                            writer.writerow(data.values())
                        elif isinstance(data, list):
                            writer.writerow(["Index", "Value"])
                            for index, value in enumerate(data):
                                writer.writerow([index, value])
                    messagebox.showinfo("Success", f"CSV file saved as {file_path}")
            else:
                messagebox.showwarning("No Data", "No data available for this key.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to download CSV: {str(e)}")
    

    def print_value(self, Sample_Name):
        try:
            res = self.Backend.NPK_prediction(Sample_Name)

            if res is not None:
                messagebox.showinfo("Value", f"NPK values of {Sample_Name}: [ {', '.join(map(str, res))} ]")

            else:
                messagebox.showwarning("No Data", f"No data available for {Sample_Name}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {str(e)}")

     




