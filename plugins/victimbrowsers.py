import os

def navegadores_instalados():
    navegadores = []

    caminhos_nav = {
        'Chrome': [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ],
        'Firefox': [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
        ],
        'Edge': [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        ],
        'Opera': [
            r"C:\Program Files\Opera\launcher.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\Opera\launcher.exe"),
        ],
        'Brave': [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\Application\brave.exe"),
        ]
    }

    for navegador, pastas in caminhos_nav.items():
        for pasta in pastas:
            if os.path.exists(pasta):
                navegadores.append(navegador)
                break
    return navegadores

if __name__ == "__main__":
    navegadores = navegadores_instalados()
    print(navegadores)
