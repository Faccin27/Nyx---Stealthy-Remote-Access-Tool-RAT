import json
import os
import tkinter as tk
from tkinter import messagebox

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.json')

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
    
    return config  

def mostrar_alerta():
    config = load_config()  
    alert_title = config.get("ALERT_TITLE", "Alert")
    alert_content = config.get("ALERT_CONTENT", "The application is not compatible with your current operating system. Please check the minimum system requirements or contact support for further assistance.")
    
    root = tk.Tk()
    root.withdraw()  
    
    messagebox.showwarning(alert_title, alert_content)
    
    root.destroy()

if __name__ == "__main__":
    mostrar_alerta()
