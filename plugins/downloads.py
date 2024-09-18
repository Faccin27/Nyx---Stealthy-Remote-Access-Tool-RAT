import os
import shutil
import sqlite3
import base64
from datetime import datetime, timedelta

class BrowserDownloadsExtractor:
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

    def get_chromium_downloads(self) -> list[tuple[str, str, str, str]]:
        download_file_paths = list()

        for root, _, files in os.walk(self.browser_path):
            for file in files:
                if file.lower() == "history":
                    filepath = os.path.join(root, file)
                    download_file_paths.append(filepath)

        download_entries = []

        for path in download_file_paths:
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
                # Consultando downloads
                results = cursor.execute(
                    "SELECT target_path, tab_url, start_time, received_bytes FROM downloads"
                ).fetchall()

                for target_path, tab_url, start_time, received_bytes in results:
                    start_time = self.chromium_time_to_datetime(start_time)
                    if target_path and tab_url and start_time:
                        download_entries.append((target_path, tab_url, start_time, received_bytes))

                download_entries.sort(key=lambda x: x[2], reverse=True)

            except Exception as e:
                print(f"Erro ao consultar banco de dados: {e}")

            cursor.close()
            db.close()
            os.remove(tempfile)

        return download_entries

    def get_firefox_downloads(self) -> list[tuple[str, str, str, str]]:
        download_entries = []

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
                            "SELECT content, url, dateAdded FROM moz_annos WHERE anno_attribute_id = (SELECT id FROM moz_anno_attributes WHERE name = 'downloads/destinationFileURI')"
                        ).fetchall()

                        for content, url, dateAdded in results:
                            dateAdded = self.firefox_time_to_datetime(dateAdded)
                            if content and url and dateAdded:
                                download_entries.append((content, url, dateAdded, None))  # Firefox doesn't store received bytes in this table

                        download_entries.sort(key=lambda x: x[2], reverse=True)

                    except Exception as e:
                        print(f"Erro ao consultar banco de dados: {e}")

                    cursor.close()
                    db.close()
                    os.remove(tempfile)

        return download_entries

    def chromium_time_to_datetime(self, timestamp: int) -> datetime:
        """Converte o timestamp do Chromium (em microssegundos desde 1601-01-01) para datetime."""
        return datetime(1601, 1, 1) + timedelta(microseconds=timestamp)

    def firefox_time_to_datetime(self, timestamp: int) -> datetime:
        """Converte o timestamp do Firefox (em microssegundos desde 1970-01-01) para datetime."""
        return datetime(1970, 1, 1) + timedelta(microseconds=timestamp)

    def get_random_string(self, length: int) -> str:
        return base64.urlsafe_b64encode(os.urandom(length)).decode()[:length]

    def save_downloads_to_file(self, downloads: list[tuple[str, str, str, str]], file_path: str) -> None:
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                for target_path, tab_url, date, received_bytes in downloads:
                    file.write(f"File: {target_path}\nURL: {tab_url}\nDate: {date.strftime('%Y-%m-%d %H:%M:%S')}\nSize: {received_bytes or 'N/A'} bytes\n\n")
            print(f"Downloads salvos em: {file_path}")
        except Exception as e:
            print(f"Erro ao salvar downloads em arquivo: {e}")

    def get_downloads(self) -> list[tuple[str, str, str, str]]:
        if self.browser_name in ["chrome", "brave", "opera", "edge"]:
            return self.get_chromium_downloads()
        elif self.browser_name == "firefox":
            return self.get_firefox_downloads()
        else:
            print(f"Navegador {self.browser_name} não suportado.")
            return []


if __name__ == "__main__":
    browsers = ["chrome", "brave", "opera", "edge", "firefox"]

    for browser in browsers:
        extractor = BrowserDownloadsExtractor(browser)
        downloads = extractor.get_downloads()

        if downloads:
            nyx_path = os.path.join(os.getenv("LOCALAPPDATA"), "Nyx")
            if not os.path.exists(nyx_path):
                os.makedirs(nyx_path)

            downloads_file_path = os.path.join(nyx_path, f"{browser}_downloads.txt")
            extractor.save_downloads_to_file(downloads, downloads_file_path)
        else:
            print(f"Nenhum download encontrado para {browser}.")
