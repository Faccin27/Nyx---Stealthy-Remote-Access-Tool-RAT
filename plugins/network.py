import socket
import requests
import uuid

def obter_informacoes_internet():
    try:
        ip = socket.gethostbyname(socket.gethostname())
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
    except Exception as e:
        ip = f"Erro ao obter IP: {e}"
        mac = "Erro ao obter MAC"

    try:
        response = requests.get('https://ipinfo.io/json')
        data = response.json()
        pais = data.get('country', 'Desconhecido')
        regiao = data.get('region', 'Desconhecida')
        cidade = data.get('city', 'Desconhecida')
        cep = data.get('postal', 'Desconhecido')
        isp = data.get('org', 'Desconhecido')
    except Exception as e:
        pais = regiao = cidade = cep = isp = f"Erro ao obter localização: {e}"

    info = (
        f"IP: {ip}\n"
        f"MAC: {mac}\n"
        f"País: {pais}\n"
        f"Região: {regiao}\n"
        f"Cidade: {cidade}\n"
        f"CEP: {cep}\n"
        f"ISP: {isp}\n"
    )
    return info

if __name__ == "__main__":
    informacoes = obter_informacoes_internet()
    print(informacoes)
