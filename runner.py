import tkinter as tk
from firebase import firebase_instance
from frontend import UI, ProcessHandler
from backend import Backend



if __name__ == "__main__":
    root = tk.Tk()
    
    process_handler = ProcessHandler(firebase_instance, root, None)  
    backend_base = Backend(firebase_instance, process_handler)  
    process_handler.Backend = backend_base 

    ui = UI(root, process_handler)
    process_handler.ui = ui  

    root.mainloop()
