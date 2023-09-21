import subprocess
import os

def compile_main():
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("PyInstaller não está instalado. Instalando...")
        subprocess.run(["pip", "install", "pyinstaller"], check=True)

    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=Build",
        "main.py",
        "--add-data", "config.json;."  # Adiciona o arquivo config.json
    ]

    command.extend([
        "--windowed",  # msm que no console, só que mais uma validação
        "--uac-admin",  # req admin privlgs
        "--hidden-import=pynput.keyboard._win32",  # Importação oculta para pynput
        "--hidden-import=pynput.mouse._win32",     # Importação oculta para pynput
    ])

    try:
        subprocess.run(command, check=True)
        print("Build criada.")
        print("O executável 'Build.exe' foi criado na pasta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a compilação: {e}")

if __name__ == "__main__":
    compile_main()
