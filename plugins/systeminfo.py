import subprocess
import psutil
import platform
import cpuinfo
import GPUtil
import uuid

def obter_informacoes_sistema():

    #  CPU
    try:
        cpu_info = cpuinfo.get_cpu_info()
        cpu = cpu_info['brand_raw'] if 'brand_raw' in cpu_info else "Desconhecido"
    except Exception as e:
        cpu = f"Erro ao obter CPU: {e}"

    #  GPU
    try:
        gpus = GPUtil.getGPUs()
        gpu = ', '.join([gpu.name for gpu in gpus]) if gpus else "Nenhuma GPU encontrada"
    except ImportError:
        gpu = "Informação de GPU não disponível"

    #  RAM
    ram = round(psutil.virtual_memory().total / (1024 ** 3), 2)

    #  HWID
    hwid = uuid.getnode()

    info = (
        f"CPU: {cpu}\n"
        f"GPU: {gpu}\n"
        f"RAM: {ram} GB\n"
        f"HWID: {hwid}\n"
    )
    return info

if __name__ == "__main__":
    informacoes = obter_informacoes_sistema()
    print(informacoes)
