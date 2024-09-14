import os
import platform
import getpass

def get_os_info():
    os_info = {
        'System': platform.system(),         
        'Version': platform.version(),       
        'Architecture': platform.architecture()[0]  
    }
    
    formatted_os_info = '\n'.join(f"{key}: {value}" for key, value in os_info.items())
    return formatted_os_info

def print_os_info():
    info = get_os_info()
    for key, value in info.items():
        print(f"{key}: {value}\n")

if __name__ == "__main__":
    print_os_info()
