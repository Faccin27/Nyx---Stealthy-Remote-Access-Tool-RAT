import subprocess
import wmi

def get_hwid() -> str:
    try:
        hwid = subprocess.check_output(
            'C:\\Windows\\System32\\wbem\\WMIC.exe csproduct get uuid',
            shell=True,
            stdin=subprocess.PIPE,
            stderr=subprocess.PIPE
        ).decode('utf-8').split('\n')[1].strip()
    except:
        hwid = "None"
    
    return hwid

def get_cpu() -> str:
    cpu = wmi.WMI().Win32_Processor()[0].Name
    return cpu

def get_ram() -> float:
    ram = round(float(wmi.WMI().Win32_OperatingSystem()[0].TotalVisibleMemorySize) / 1048576, 0)
    return ram

def get_gpu() -> str:
    gpu = wmi.WMI().Win32_VideoController()[0].Name
    return gpu

def get_system_info() -> str:
    hwid = get_hwid()
    cpu = get_cpu()
    ram = get_ram()
    gpu = get_gpu()

    info = (
        f"CPU: {cpu}\n"
        f"GPU: {gpu}\n"
        f"RAM: {ram} GB\n"
        f"HWID: {hwid}\n"
    )
    
    return info

# Exemplo de uso
system_info = get_system_info()
print(system_info)
