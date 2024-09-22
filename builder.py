import subprocess
import os
import json
import inquirer

def load_config():
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

def select_options(config):
    questions = [
        inquirer.Checkbox('options',
                          message="Tools:",
                          choices=list(config.keys()),
                          default=[key for key, value in config.items() if value]
                          ),
    ]
    answers = inquirer.prompt(questions)
    
    for key in config.keys():
        config[key] = key in answers['options']

def compile_main(config):
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("PyInstaller não está instalado. Instalando...")
        subprocess.run(["pip", "install", "pyinstaller"], check=True)

    save_config(config)

    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--name=Build",
        "main.py",
        "--add-data", "config.json;."
    ]

    command.extend([
        "--windowed",
        "--uac-admin",
        "--hidden-import=pynput.keyboard._win32",
        "--hidden-import=pynput.mouse._win32",
    ])

    try:
        subprocess.run(command, check=True)
        print("Build criada.")
        print("O executável 'Build.exe' foi criado na pasta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a compilação: {e}")

if __name__ == "__main__":
    config = load_config()
    select_options(config)
    compile_main(config)
